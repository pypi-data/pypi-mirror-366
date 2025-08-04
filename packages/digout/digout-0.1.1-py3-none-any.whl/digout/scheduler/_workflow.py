"""Provides utility functions for processing chunked workflows.

This module contains helpers used by schedulers to determine which parts
of a chunked workflow require execution.
"""

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, Any

from tqdm.auto import tqdm

if TYPE_CHECKING:
    from ..core.workflow import ChunkWorkflow

logger = getLogger(__name__)


def get_chunk_indices_to_run(workflow: ChunkWorkflow[Any, Any]) -> list[int]:
    """Filter a workflow to find the indices of chunks that need to be run.

    This function iterates through all chunks in the workflow and checks if
    each one requires execution. A chunk is considered runnable if its
    corresponding subgraph of steps is not
    :py:attr:`~digout.core.workflow.ChunkWorkflow.empty`,
    which means it has steps that need to be executed.

    Args:
        workflow: The chunked workflow to inspect.

    Returns:
        A list of integer indices for the chunks that require execution.
    """
    logger.debug("Checking which chunks need to be run.")
    n_initial_chunks = workflow.n_chunks
    chunk_indices = [
        chunk_idx
        for chunk_idx in tqdm(
            range(n_initial_chunks), desc="Checking chunks to run", unit="chunk"
        )
        if not workflow.select_chunk(chunk_idx, reduce=True).empty
    ]
    if (n_chunks := len(chunk_indices)) < n_initial_chunks:
        logger.info(
            "Found %d chunks to run out of %d initial chunks.",
            n_chunks,
            n_initial_chunks,
        )
    else:
        logger.info("All chunks (%d) need to be run.", n_chunks)

    return chunk_indices
