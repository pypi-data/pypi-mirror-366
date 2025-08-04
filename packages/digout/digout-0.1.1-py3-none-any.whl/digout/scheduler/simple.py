"""Provides a scheduler that runs workflow chunks in memory."""

from __future__ import annotations

from functools import partial
from logging import getLogger
from typing import TYPE_CHECKING, Any

from pydantic import ConfigDict

from ._multiproc import WithMPMixin

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ..core.orchestrator import OrchestratorProtocol
    from ..core.step import StepKey
    from ..core.workflow import ChunkWorkflow

__all__ = ["SimpleScheduler"]

logger = getLogger(__name__)


def _run_chunk(
    chunk_idx: int,
    *,
    orchestrator: OrchestratorProtocol,
    workflow: ChunkWorkflow[Any, Any],
    return_output: bool = False,
) -> Mapping[StepKey, object] | None:
    """Run the orchestrator for a single workflow chunk.

    This function is designed to be the target for a parallel process. It selects
    the specified chunk from the workflow and executes it using the provided
    orchestrator.

    Args:
        chunk_idx: The index of the chunk to run.
        orchestrator: The orchestrator instance to use for execution.
        workflow: The main chunked workflow object.
        return_output: If ``True``, return the orchestrator's output.

    Returns:
        The output from the orchestrator if ``return_output`` is ``True``, otherwise
        ``None``.
    """
    logger.info("Select chunk %d.", chunk_idx)
    output = orchestrator.run(workflow.select_chunk(chunk_idx))
    return output if return_output else None


class SimpleScheduler(WithMPMixin):
    """A scheduler that runs chunks in parallel using local processes.

    This scheduler operates directly on the live workflow object in memory. It
    uses the :py:class:`~digout.scheduler._multiproc.WithMPMixin` mixin
    to distribute the execution of each chunk to a pool of worker processes.

    Unlike :py:class:`~digout.scheduler.local.LocalScheduler`, it does not serialize
    the workflow to a file first.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    return_output: bool = False
    """If True, the results from each chunk's execution are collected and returned."""

    def run(
        self, workflow: ChunkWorkflow[Any, Any], orchestrator: OrchestratorProtocol, /
    ) -> list[Mapping[StepKey, object]] | None:
        """Schedule the execution of the workflow across all chunks.

        Args:
            workflow: The workflow to run.
            orchestrator: The orchestrator to use for executing each chunk.

        Returns:
            A list containing the output from each chunk's execution if
            :py:attr:`~SimpleScheduler.return_output` is ``True``, otherwise ``None``.
        """
        n_chunks = workflow.n_chunks

        if n_chunks == 0:  # pragma: no cover
            logger.warning("No chunks to run in workflow, skipping scheduling.")
            return None

        logger.info("Scheduling %d chunks.", n_chunks)

        func = partial(
            _run_chunk,
            orchestrator=orchestrator,
            workflow=workflow,
            return_output=self.return_output,
        )

        output = self._process_map(
            func, range(n_chunks), desc="Running chunks", unit="chunk"
        )

        logger.info("Simple scheduler finished running all chunks.")
        return output if self.return_output else None  # type: ignore[return-value]

    @classmethod
    def get_key(cls) -> str:
        """Return the key for this scheduler, ``simple``."""
        return "simple"
