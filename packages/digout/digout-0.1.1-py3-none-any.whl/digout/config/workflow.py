"""Defines the main Pydantic model for a complete workflow configuration.

This module provides :py:class:`WorkflowConfig`, the central class for parsing and
validating a complete workflow from configuration files. It uses the registries
from its :py:attr:`WorkflowConfig.context` attribute to instantiate all the necessary
components (steps, streams, orchestrator, etc.) and assembles them
into a runnable object.
"""

from __future__ import annotations

from functools import cached_property
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Any, TypeVar

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationInfo,
    WithJsonSchema,
    field_validator,
)

from .._utils.path import PathLike, ResolvedPath  # noqa: TC001 (needed by Pydantic)
from ..context import Context
from ..core.orchestrator import OrchestratorProtocol
from ..core.runner import Runner
from ..core.scheduler import SchedulerProtocol
from ..core.step import StepKey, StepProtocol  # noqa: TC001 (needed by Pydantic)
from ..core.workflow import GenericWorkflow
from ..registry import OrchestratorKey, SchedulerKey  # noqa: TC001 (needed by Pydantic)
from ._context import pydantic_validate_mapping_from_context_registry
from ._io import YAMLMixin
from ._version import VersionMixin

if TYPE_CHECKING:
    from collections.abc import Mapping

__all__ = ["RuntimeConfig", "WorkflowConfig"]

logger = getLogger(__name__)


V = TypeVar("V")


def _get_object(
    *, mapping: Mapping[str, V], key: str | None, mapping_name: str
) -> V | None:
    """Select an object from a mapping by its key.

    Args:
        mapping: The mapping of available objects.
        key: The key of the object to select.
        mapping_name: A human-readable name for the mapping, used in error messages.

    Returns:
        The selected object, or ``None`` if the key is ``None``.

    Raises:
        KeyError: If the provided key is not found in the mapping.
    """
    if key is None:
        return None
    try:
        return mapping[key]
    except KeyError as e:
        msg = (
            f"{mapping_name} with key {key!r} not found in the "
            f"available {mapping_name}s. Available keys: "
            + ", ".join(map(repr, mapping.keys()))
        )
        raise KeyError(msg) from e


class RuntimeConfig(BaseModel):
    """A model for runtime-specific configuration choices.

    This includes which steps to execute and which backends to use.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    stream_orchestrator_key: OrchestratorKey | None = None
    """The key of the orchestrator to use for the initial stream-processing phase."""

    chunk_orchestrator_key: OrchestratorKey | None = None
    """The key of the orchestrator to use for the main chunk-processing phase."""

    scheduler_key: SchedulerKey | None = None
    """The key of the scheduler that manages the execution of all chunks."""

    required_keys: set[StepKey] = Field(default_factory=set)
    """A set of step keys identifying the final workflow outputs to produce."""


class WorkflowConfig(VersionMixin, YAMLMixin):
    """A complete, validated, and runnable workflow configuration.

    This class is the main entry point for parsing a workflow from configuration
    files. It is responsible for instantiating all components (steps, streams,
    and execution backends) and assembling them into a final, executable
    :py:class:`~digout.core.runner.Runner` object.

    Architecturally, this class separates the definition of available components from
    their usage. The :py:attr:`steps`, :py:attr:`schedulers`,
    and :py:attr:`orchestrators` dictionaries contain all components
    that *could* be used.
    The :py:attr:`runtime` configuration then
    acts as a "control panel", selecting which components are active for a specific
    run by referencing their keys.

    During validation, the component objects in the :py:attr:`schedulers`,
    :py:attr:`orchestrators`, :py:attr:`steps`, and :py:attr:`streams`
    dictionaries are instantiated and validated using the corresponding
    :py:attr:`~digout.context.Context.registries` found in the :py:attr:`context`
    attribute.
    If a registry for a component type is not provided in the context,
    its objects are not validated and are used as-is.
    """

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    context: Context = Field(default_factory=Context)
    """The context for the workflow, providing shared registries and placeholders."""

    steps: dict[StepKey, Annotated[StepProtocol[Context, Any], WithJsonSchema({})]] = (
        Field(default_factory=dict)
    )
    """A dictionary of all step configurations, keyed by their unique identifiers."""

    schedulers: dict[SchedulerKey, Annotated[SchedulerProtocol, WithJsonSchema({})]] = (
        Field(default_factory=dict)
    )
    """A dictionary of all available scheduler implementations."""

    orchestrators: dict[
        OrchestratorKey, Annotated[OrchestratorProtocol, WithJsonSchema({})]
    ] = Field(default_factory=dict)
    """A dictionary of all available orchestrator implementations."""

    streams: dict[StepKey, object] = Field(default_factory=dict)
    """A dictionary of pre-materialized streams, keyed by the step that produces them."""  # noqa: E501

    runtime: RuntimeConfig = Field(default_factory=RuntimeConfig)
    """Runtime choices, such as which targets and backends to use."""

    workflow_path: ResolvedPath | None = None
    """Optional path for saving this config via the :py:meth:`save_workflow` method."""

    # Validators =====================================================================
    @field_validator(
        "steps",
        "schedulers",
        "orchestrators",
        "streams",
        mode="before",
        json_schema_input_type=Any,
    )
    @classmethod
    def _validate_components(cls, v: object, info: ValidationInfo) -> object:
        """Validate object mappings from the context registry."""
        return pydantic_validate_mapping_from_context_registry(v, info)

    # Properties =====================================================================
    # Back-end selection -------------------------------------------------------------
    @cached_property
    def stream_orchestrator(self) -> OrchestratorProtocol | None:
        """The selected orchestrator for the stream phase, based on ``runtime.stream_orchestrator_key``."""  # noqa: E501
        return _get_object(
            mapping=self.orchestrators,
            key=self.runtime.stream_orchestrator_key,
            mapping_name="orchestrator",
        )

    @cached_property
    def chunk_orchestrator(self) -> OrchestratorProtocol | None:
        """The selected orchestrator for the chunk phase, based on ``runtime.chunk_orchestrator_key``."""  # noqa: E501
        return _get_object(
            mapping=self.orchestrators,
            key=self.runtime.chunk_orchestrator_key,
            mapping_name="chunk orchestrator",
        )

    @cached_property
    def scheduler(self) -> SchedulerProtocol | None:
        """The selected scheduler instance, based on ``runtime.scheduler_key``."""
        return _get_object(
            mapping=self.schedulers,
            key=self.runtime.scheduler_key,
            mapping_name="scheduler",
        )

    # Most important property --------------------------------------------------------
    def save_workflow(self, output_path: PathLike | None = None) -> None:
        """Save the current workflow configuration to a YAML file.

        The file is saved to the path provided as an argument, falling back to
        the path specified in the :py:attr:`workflow_path` attribute. If no path is
        available, a warning is logged and nothing is saved.

        Args:
            output_path: An optional path to save the file to. If provided, it
                overrides the instance's :py:attr:`workflow_path` attribute.
        """
        if output_path is None:
            output_path = self.workflow_path
            exclude_workflow_path = True
        else:
            exclude_workflow_path = False

        if output_path is None:
            logger.warning("No workflow path specified. Skipping saving the workflow.")
            return

        output_path = Path(output_path).expanduser().resolve()
        # Drop the `workflow_path` field in the dumped YAML
        self.to_yaml(
            output_path,
            pydantic_kwargs=(
                {"exclude": {"workflow_path"}} if exclude_workflow_path else None
            ),
        )
        logger.info("Workflow configuration saved to '%s'", output_path)

    @cached_property
    def runner(
        self,
    ) -> Runner[
        OrchestratorProtocol, OrchestratorProtocol, SchedulerProtocol, Context, Context
    ]:
        """The final, executable object built from this configuration.

        This property is the main product of the this class. It
        assembles the dependency graph from the defined steps and streams and
        combines it with the selected execution backends (orchestrator and scheduler)
        into a ready-to-use :py:class:`~digout.core.runner.Runner` instance.
        """
        return Runner[
            OrchestratorProtocol,
            OrchestratorProtocol,
            SchedulerProtocol,
            Context,
            Context,
        ](
            workflow=GenericWorkflow[Context, Context].from_steps(
                steps=self.steps,
                required_keys=self.runtime.required_keys,
                sources=self.streams,
                context=self.context,
            ),
            stream_orchestrator=self.stream_orchestrator,
            chunk_orchestrator=self.chunk_orchestrator,
            scheduler=self.scheduler,
        )
