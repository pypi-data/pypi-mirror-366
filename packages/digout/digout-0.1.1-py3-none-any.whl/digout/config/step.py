"""Defines a Pydantic model for a single, fully-validated step configuration."""

from __future__ import annotations

from collections.abc import Mapping
from logging import DEBUG, getLogger
from typing import TYPE_CHECKING, Annotated, Any

from pydantic import ConfigDict, Field, WithJsonSchema, model_validator

from ..context._context import Context
from ..core.step import StepKey, StepKind, StepProtocol
from ._io import YAMLMixin
from ._version import VersionMixin

if TYPE_CHECKING:
    from ..registry import Registry

logger = getLogger(__name__)

__all__ = ["StepConfig"]


def _validate_config(
    config: Mapping[str, Any],
) -> tuple[Context, StepKey, object, Mapping[str, Any]]:
    """Extract and perform basic validation on the main fields of a step configuration."""  # noqa: E501
    config = dict(config)

    context = Context.model_validate(config.pop("context", {}))
    if not isinstance(context, Context):
        msg = f"Expected 'context' to be a {Context!r}, got: {type(context).__name__}."
        raise ValueError(msg)  # noqa: TRY004 (ValueError for pydantic validation)

    step_key = config.pop("step_key", None)
    if not step_key:
        msg = "Missing 'step_key' in step configuration."
        raise ValueError(msg)
    if not isinstance(step_key, StepKey):
        msg = (
            f"Expected 'step_key' to be a {StepKey!r}, got: {type(step_key).__name__}."
        )
        raise ValueError(msg)  # noqa: TRY004 (ValueError for pydantic validation)

    step = config.pop("step", {})

    sources = config.pop("sources", {})
    if not isinstance(sources, Mapping):
        msg = f"Expected 'sources' to be a Mapping, got: {type(sources).__name__}."
        raise ValueError(msg)  # noqa: TRY004 (ValueError for pydantic validation)

    if config:
        msg = (
            "Unexpected fields in step configuration: "
            + ", ".join(map(repr, config.keys()))
            + ". Expected fields: 'step_key', 'step', 'sources'."
        )
        raise ValueError(msg)

    return context, step_key, step, sources


def _validate_source_keys(
    source_keys: set[StepKey], expected_source_keys: set[StepKey]
) -> None:
    """Ensure the provided source keys exactly match the step's dependencies."""
    if expected_source_keys != source_keys:
        msg = (
            "Expected sources: " + ", ".join(map(repr, expected_source_keys)) + ". "
            "Found sources: " + ", ".join(map(repr, source_keys)) + ". "
            "Please ensure the sources match the expected keys."
        )
        raise ValueError(msg)


def _get_source_registry(
    step_kind: StepKind, context: Context
) -> Registry[StepKey, Any] | None:
    """Get the appropriate registry for a step's sources based on its kind.

    - A :py:attr:`digout.core.step.StepKind.STREAM` step's sources are assumed to be
      streams and are validated against the ``stream`` registry.
    - A :py:attr:`digout.core.step.StepKind.CHUNK` step's sources are assumed to be
      chunks and are validated against the ``chunk`` registry.

    Args:
        step_kind: The kind of the step whose sources are being validated.
        context: The workflow context containing the registries.

    Returns:
        The relevant registry (either "stream" or "chunk"), or ``None`` if not found.
    """
    if step_kind == StepKind.STREAM:
        return context.registries.get("stream")
    elif step_kind == StepKind.CHUNK:
        return context.registries.get("chunk")
    else:  # pragma: no cover (unreachable)
        msg = f"Unsupported step kind: {step_kind}"
        raise ValueError(msg)


class StepConfig(VersionMixin, YAMLMixin):
    """A fully-validated configuration for a single workflow step.

    This model represents a step after its configuration and its dependencies
    (sources) have been validated and instantiated using the registries from the
    workflow's context.
    It encapsulates a runnable :py:class:`digout.core.step.StepProtocol` object and
    its ready-to-use inputs.
    """

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    context: Context = Field(default_factory=Context)
    """The workflow context, providing access to registries and placeholders."""

    step_key: StepKey
    """The unique identifier for this step."""

    step: Annotated[StepProtocol[Context, Any], WithJsonSchema({})]
    """The step object.

    The latter is validated against step registry stored
    in the context's :py:attr:`~digout.context.Context.registries` field
    given the provided :py:attr:`step_key`.

    Please check the documentation of the the :py:mod:`~digout.core.step`
    being instantiated for more information on the step's
    configuration and its expected parameters.
    """

    sources: dict[str, Any] = Field(default_factory=dict)
    """A dictionary of the step's instantiated dependencies (its sources).

    The keys are the source names returned by the step's
    :py:meth:`~digout.core.step.StepProtocol.get_source_keys` method.

    The values are the instantiated source objects of the step.

    * For a :py:class:`digout.core.step.StepKind.STREAM` step, these are streams-like
      objects.
    * For a :py:class:`digout.core.step.StepKind.CHUNK` step, these are chunk-like
      objects.

    The sources are validated against the relevant registry
    (either "stream" or "chunk") in the :py:attr:`~digout.context.Context.registries`
    field of the context.
    """

    # Validators =====================================================================
    @model_validator(mode="before")
    @classmethod
    def _validate_all_fields(cls, values: Mapping[str, Any]) -> dict[str, Any]:
        """Validate ``context``, ``step_key``, ``step``, and ``sources``."""
        context, step_key, step_config, sources = _validate_config(values)

        step_registry: Registry[StepKey, StepProtocol[Context, Any]] | None = (
            context.registries.get("step")
        )

        if step_registry is None:
            if logger.isEnabledFor(DEBUG):
                logger.debug(
                    "The step registry is not available in the context. "
                    "Skipping the validation of the step configuration "
                    "and sources."
                )
            return {"step_key": step_key, "step": step_config, "sources": sources}

        step = step_registry.instantiate(step_key, step_config)
        source_keys = set(sources.keys())
        _validate_source_keys(source_keys, set(step.get_source_keys()))

        source_registry = _get_source_registry(step.kind, context)
        if source_registry is None:
            if logger.isEnabledFor(DEBUG):
                logger.debug(
                    "No source registry found for step kind '%s'. "
                    "Skipping source validation.",
                    step.kind,
                )
            return {"step_key": step_key, "step": step, "sources": sources}

        sources = source_registry.instantiate_many(sources)
        return {
            "context": context,
            "step_key": step_key,
            "step": step,
            "sources": sources,
        }

    # Public methods =================================================================
    def run(self) -> object:
        """Call the :py:meth:`~digout.core.step.StepProtocol.run` method of the step.

        It simply runs:

        .. code-block:: python

            self.step.run(self.sources, self.context)

        Returns:
            The step's target,
            as returned by the step's :py:meth:`~digout.core.step.StepProtocol.run`
            method.
        """
        return self.step.run(self.sources, self.context)

    def has_run(self) -> bool:
        """Call the :py:meth:`~digout.core.step.StepProtocol.has_run` method of the step.

        It simply runs:

        .. code-block:: python

            self.step.has_run(self.context)

        Returns:
            ``True`` if the step has already produced its target,
            ``False`` otherwise.
        """  # noqa: E501
        return self.step.has_run(self.context)
