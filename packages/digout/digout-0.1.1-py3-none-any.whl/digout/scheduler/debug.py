"""Provides a debug scheduler for inspecting chunked workflows."""

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict
from tqdm.auto import tqdm

if TYPE_CHECKING:
    from ..core.orchestrator import OrchestratorProtocol
    from ..core.workflow import ChunkWorkflow

__all__ = ["DebugScheduler"]

logger = getLogger(__name__)


class DebugScheduler(BaseModel):
    """A scheduler that inspects which chunks would run, without executing them.

    This scheduler identifies all runnable chunks in a workflow but does not pass
    them to the orchestrator for execution. Instead, it logs information about
    the chunks that would be processed, making it a useful tool for debugging.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    show_context: bool = True
    """Whether to show the context of each chunk that would be run."""

    def run(self, workflow: ChunkWorkflow[Any, Any], _: OrchestratorProtocol, /) -> Any:
        """Identify and log runnable chunks instead of executing them.

        This method determines which chunks have not yet been completed. It then
        logs the context of each of these runnable chunks. The provided
        orchestrator is ignored.

        Args:
            workflow: The chunked workflow to inspect.
            _: The orchestrator, which is ignored by this scheduler.

        Returns:
            A dictionary mapping the index of each runnable chunk to its context.
        """
        n_initial_chunks = workflow.n_chunks
        chunk_contexts = {
            chunk_idx: runnable_workflow.context
            for chunk_idx in tqdm(
                range(n_initial_chunks), desc="Checking chunks to run", unit="chunk"
            )
            if not (
                runnable_workflow := workflow.select_chunk(chunk_idx, reduce=True)
            ).empty
        }
        if (n_chunks := len(chunk_contexts)) < n_initial_chunks:
            logger.info(
                "Found %d chunks to run out of %d initial chunks.",
                n_chunks,
                n_initial_chunks,
            )
        else:
            logger.info("All chunks (%d) need to be run.", n_chunks)

        if self.show_context and chunk_contexts:
            logger.info("Chunk contexts:")
            for chunk_idx, context in chunk_contexts.items():
                logger.info("- %d: %s", chunk_idx, context)

        return chunk_contexts

    @classmethod
    def get_key(cls) -> str:
        """Return the key for this scheduler, ``debug``."""
        return "debug"
