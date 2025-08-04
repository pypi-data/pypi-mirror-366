"""Provide a scheduler that runs workflow chunks on the local machine."""

from __future__ import annotations

from functools import partial
from logging import getLogger
from typing import TYPE_CHECKING, Any

from .._utils.logging import DEFAULT_LOG_LEVEL, LogLevel
from ..environment import execute
from ._base import SchedulerBase, get_orchestrate_workflow_args
from ._multiproc import WithMPMixin

if TYPE_CHECKING:
    from pathlib import Path

    from ..core.workflow import ChunkWorkflow
    from ..registry import SchedulerKey

__all__ = ["LocalScheduler"]

logger = getLogger(__name__)


def _orchestrate_workflow(
    chunk_idx: int, *, workflow_path: str | Path, log_level: str, **kwargs: Any
) -> None:
    """Execute the orchestration script for a single workflow chunk.

    This function is designed to be the target for a parallel process, taking a
    chunk index and executing the corresponding part of the workflow defined in
    the serialized configuration file.

    Args:
        chunk_idx: The index of the chunk to process.
        workflow_path: Path to the serialized workflow configuration file.
        log_level: The logging level to use for the subprocess.
        **kwargs: Additional keyword arguments passed to the `execute` function.
    """
    execute(
        get_orchestrate_workflow_args(
            workflow_path=workflow_path, chunk_idx=chunk_idx, log_level=log_level
        ),
        **kwargs,
    )


class LocalScheduler(WithMPMixin, SchedulerBase):
    """A scheduler that runs workflow chunks in parallel on the local machine.

    This scheduler follows the :py:class:`~digout.scheduler._base.SchedulerBase``
    pattern of first serializing the workflow to a file.

    It then uses the :py:class:`~digout.scheduler._multiproc.WithMPMixin` mixin
    to launch multiple local subprocesses, with each process executing one chunk
    of the workflow.
    """

    log_level: LogLevel = DEFAULT_LOG_LEVEL
    """Logging level for running a workflow."""

    def _schedule(
        self, workflow_path: str | Path, workflow: ChunkWorkflow[Any, Any]
    ) -> None:
        """Schedules the workflow by running each chunk in a local process pool.

        Args:
            workflow_path: Path to the serialized workflow configuration file.
            workflow: The workflow object, used to get the number of chunks.
        """
        func = partial(
            _orchestrate_workflow, workflow_path=workflow_path, log_level=self.log_level
        )

        self._process_map(
            func, range(workflow.n_chunks), desc="Running chunks", unit="chunk"
        )

        logger.info("Local scheduler finished running all chunks.")

    @classmethod
    def get_key(cls) -> SchedulerKey:
        """Return the key for this scheduler, ``local``."""
        return "local"
