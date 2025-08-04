"""Provides a base class for schedulers that run workflows in external processes.

This module defines :py:class:`~digout.scheduler.SchedulerBase`, which implements
a common pattern forschedulers that need to run outside the main Python process
(e.g., on a batch system).

The pattern involves:

1.  Creating a self-contained, serializable
    :py:class:`~digout.config.workflow.WorkflowConfig` object.
2.  Saving this configuration to a YAML file.
3.  Requiring a subclass to implement the :py:meth:`~SchedulerBase._schedule` method,
    which defines how to launch external jobs that run the workflow from that file.

The :py:func:`get_orchestrate_workflow_args` function is provided to help build
command-line arguments for running the workflow in a subprocess.
"""

from __future__ import annotations

import sys
from abc import abstractmethod
from contextlib import contextmanager
from logging import getLogger
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict

from .._utils.path import ResolvedPath  # noqa: TC001 (needed by Pydantic)
from ..context import Context
from ..registry import Registries, WithKeyProtocol

if TYPE_CHECKING:
    from collections.abc import Generator

    from ..config.workflow import WorkflowConfig
    from ..core.orchestrator import OrchestratorProtocol
    from ..core.step import StepKey, StepProtocol
    from ..core.workflow import ChunkWorkflow

__all__ = ["SchedulerBase", "get_orchestrate_workflow_args"]

logger = getLogger(__name__)

_unset = object()
""" Sentinel value to indicate an unset value in a dictionary."""


def get_orchestrate_workflow_args(
    workflow_path: str | Path, chunk_idx: object, log_level: str
) -> list[str]:
    """Build the command-line arguments to run a workflow via a script.

    Args:
        workflow_path: Path to the workflow configuration file.
        chunk_idx: The index of the chunk to process.
        log_level: The logging level for the workflow run.

    Returns:
        A list of command-line arguments for executing the workflow.
    """
    return [
        sys.executable,
        "-m",
        "digout.script.digout",
        "--log-level",
        log_level,
        "orchestrate",
        "--config",
        str(workflow_path),
        "--chunk-idx",
        str(chunk_idx),
    ]


def _get_workflow_config(
    workflow: ChunkWorkflow[Any, Any], orchestrator: OrchestratorProtocol
) -> WorkflowConfig:
    """Create a self-contained ``WorkflowConfig`` from a live workflow.

    This prepares the workflow for serialization by stripping out components
    that are not needed for a remote orchestration task (e.g., the scheduler
    itself), ensuring the configuration is minimal and complete.

    Args:
        workflow: The live workflow instance.
        orchestrator: The orchestrator that will be used for execution.

    Returns:
        A serializable workflow configuration object.

    Raises:
        TypeError: If the orchestrator does not support being identified by a
            key via the :py:class:`~digout.registry.WithKeyProtocol` interface.
    """
    from ..config.workflow import RuntimeConfig, WorkflowConfig  # noqa: PLC0415

    graph = workflow.graph
    target_step_keys = {node for node in graph.nodes if graph.out_degree(node) == 0}

    if not isinstance(orchestrator, WithKeyProtocol):
        msg = (
            f"Scheduler requires an orchestrator "
            "that implements WithKeyProtocol to run the workflow, "
            "but the provided orchestrator does not: "
            f"{orchestrator.__class__.__name__}"
        )
        raise TypeError(msg)

    context = workflow.context
    assert isinstance(context, Context)

    orchestrator_key = orchestrator.get_key()
    steps: dict[StepKey, StepProtocol[Any, Context]] = {
        step_key: step
        for step_key, data in graph.nodes(data=True)
        if (step := data.get("step", _unset)) is not _unset
    }
    #: Registry names to keep in the workflow configuration.
    #: Other registries are dropped because they aren't used by the orchestrator.
    registries: Registries[Context] = {
        registry_name: registry
        for registry_name in ("step", "stream", "orchestrator")
        if (registry := context.registries.get(registry_name)) is not None
    }  # type: ignore[assignment]
    context = Context(registries=registries, placeholders=context.placeholders)
    streams: dict[StepKey, object] = {
        step_key: target
        for step_key, data in graph.nodes(data=True)
        if (target := data.get("target", _unset)) is not _unset
    }
    runtime_config = RuntimeConfig(
        required_keys=target_step_keys, chunk_orchestrator_key=orchestrator_key
    )
    return WorkflowConfig(
        steps=steps,
        context=context,
        # Schedulers are not needed for pure orchestration.
        schedulers={},
        streams=streams,
        orchestrators={orchestrator_key: orchestrator},
        runtime=runtime_config,
    )


class SchedulerBase(BaseModel):
    """An abstract base class for schedulers that run workflows externally.

    This class provides the core logic for serializing a workflow to a file.
    Subclasses must implement the ``_schedule`` method to define the specific
    mechanism for launching jobs (e.g., local subprocesses, a batch system).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    workflow_path: ResolvedPath | None = None
    """The file path for saving the workflow configuration.

    If not provided, a temporary file path will be used.
    """

    @contextmanager
    def _get_workflow_path(self) -> Generator[Path, None, None]:
        """Provide a path for the workflow configuration file.

        This context manager yields a path, creating a temporary one if
        ``workflow_path`` is not set. The path is resolved to be absolute.

        Yields:
            The path to the workflow configuration file.
        """
        if (workflow_path := self.workflow_path) is not None:
            yield Path(workflow_path.as_posix()).expanduser().resolve()
        else:
            with TemporaryDirectory() as tmpdir:
                workflow_path = Path(tmpdir) / "workflow.yaml"
                logger.debug("Using temporary workflow path: %s", workflow_path)
                yield workflow_path

    @contextmanager
    def _save_workflow_config(
        self, workflow_config: WorkflowConfig
    ) -> Generator[Path, None, None]:
        """Save the workflow configuration and yields the path to the file.

        Args:
            workflow_config: The workflow configuration to save.

        Yields:
            The path where the workflow configuration was saved.
        """
        with self._get_workflow_path() as workflow_path:
            if workflow_path.exists():
                logger.info(
                    "Workflow configuration already exists at %s. "
                    "Overwriting it with the new configuration.",
                    workflow_path,
                )

            workflow_config.to_yaml(workflow_path)
            yield workflow_path

    def run(
        self, workflow: ChunkWorkflow[Any, Any], orchestrator: OrchestratorProtocol, /
    ) -> None:
        """Serialize and run the workflow using the :py:meth:`_schedule` method.

        This method orchestrates the external execution process. It first
        creates a serializable configuration from the live workflow, saves it
        to a file, and then delegates to the :py:meth:`_schedule` method to handle
        the actual job submission.

        Args:
            workflow: The workflow to execute.
            orchestrator: The orchestrator to use for running each chunk.
        """
        workflow_config = _get_workflow_config(
            workflow=workflow, orchestrator=orchestrator
        )
        n_chunks = workflow.n_chunks
        with self._save_workflow_config(workflow_config) as workflow_path:
            logger.info(
                "Running workflow with %d chunks using %s scheduler.",
                n_chunks,
                self.__class__.__name__,
            )
            return self._schedule(workflow_path, workflow)

    @abstractmethod
    def _schedule(self, workflow_path: Path, workflow: ChunkWorkflow[Any, Any]) -> None:
        """Schedule the execution of the workflow.

        Subclasses must implement this method to define how to run the workflow
        for all its chunks. A typical implementation will loop from chunk index
        0 to N-1 and launch a job for each. The :py:func:`get_orchestrate_workflow_args`
        function can be used to build the command for each job.

        Args:
            workflow_path: The absolute path to the serialized workflow config.
            workflow: The workflow object, used to get properties like the
                total number of chunks.
        """
        ...
