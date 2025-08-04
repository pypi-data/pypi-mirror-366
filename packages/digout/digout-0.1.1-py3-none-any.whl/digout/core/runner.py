"""High-level *runner* that drives a :py:class:`~digout.core.workflow.GenericWorkflow`.

The runner coordinates three components:

* a **generic workflow** containing both stream and chunk steps;
* an **orchestrator** that can execute any
  :py:class:`~digout.core.workflow.RunnableWorkflow`;
* an optional **scheduler** that can parallelise execution of the many per-chunk
  workflows produced from the generic workflow.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import cached_property
from logging import getLogger
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from digout.core._graph.base import collect_targets

from .orchestrator import OrchestratorProtocol
from .scheduler import SchedulerProtocol

if TYPE_CHECKING:
    from collections.abc import Mapping

    from .context import ContextProtocol
    from .step import StepKey
    from .workflow import ChunkWorkflow, GenericWorkflow, RunnableWorkflow


logger = getLogger(__name__)

__all__ = ["Runner"]


SOR = TypeVar("SOR", bound=OrchestratorProtocol)
"""Type variable for the orchestrator type, a subclass of OrchestratorProtocol."""

COR = TypeVar("COR", bound=OrchestratorProtocol)
"""Type variable for the orchestrator type, a subclass of OrchestratorProtocol."""

SH = TypeVar("SH", bound=SchedulerProtocol)
"""Type variable for the scheduler type, a subclass of SchedulerProtocol."""

C_stream = TypeVar("C_stream", bound="ContextProtocol")
"""Type variable for the context type of stream steps."""

C_chunk = TypeVar("C_chunk", bound="ContextProtocol")
"""Type variable for the context type of chunk steps."""


@dataclass
class Runner(Generic[SOR, COR, SH, C_stream, C_chunk]):
    """Orchestrates a full run of a :py:class:`~digout.core.workflow.GenericWorkflow`.

    The runner is responsible for:

    1. Extracting the **stream workflow** from the generic workflow
       via :py:meth:`digout.core.workflow.GenericWorkflow.to_stream`
    2. Running the **stream phase** exactly once and caching the resulting
       **stream targets**.
    3. Preparing the **chunk workflow** by injecting back the cached stream targets
       into the generic workflow with the
       :py:meth:`digout.core.workflow.GenericWorkflow.to_chunk` method,
       yielding a :py:class:`digout.core.workflow.ChunkWorkflow`.
    4. Running the **chunk phase** either

        - for a single chunk via :py:meth:`orchestrate_chunk`, or
        - for all chunks via :py:meth:`schedule`.
    """

    workflow: GenericWorkflow[C_stream, C_chunk]
    """The original workflow containing both stream and chunk steps."""

    stream_orchestrator: SOR | None = None
    """Component that executes a runnable workflow for the stream phase.

    May be ``None`` if the stream phase does not need to be run.
    """

    chunk_orchestrator: COR | None = None
    """Component that executes a runnable workflow for *one* chunk DAG.

    May be ``None`` for a stream-only execution without chunking.
    It could be the same as the stream orchestrator,
    but it has to be repeated.
    """

    scheduler: SH | None = None
    """Component that distributes chunk workflows.

    May be ``None`` for single-chunk execution.
    """

    _stream_targets: Mapping[StepKey, object] | None = field(default=None, init=False)
    """Cache for the outputs of the stream phase."""

    _chunk_workflow: ChunkWorkflow[C_stream, C_chunk] | None = field(
        default=None, init=False
    )
    """Cache for the prepared :py:class:`digout.core.workflow.ChunkWorkflow`."""

    @cached_property
    def stream_workflow(self) -> RunnableWorkflow[C_stream]:
        """Return the runnable stream workflow.

        The stream workflow is extracted from the generic workflow
        by calling the :py:meth:`~digout.core.workflow.GenericWorkflow.to_stream`
        method.
        """
        return self.workflow.to_stream()

    # Private methods ===============================================================
    def _prepare_chunk_workflow(self) -> ChunkWorkflow[C_stream, C_chunk]:
        """Build and cache the :py:class:`ChunkWorkflow`.

        * Runs the stream phase (if not already cached).
        * Calls :py:meth:`digout.core.workflow.GenericWorkflow.to_chunk`.
        """
        if (chunk_workflow := self._chunk_workflow) is not None:
            logger.debug("Chunk workflow already prepared, returning cached value.")
            return chunk_workflow

        stream_targets = self.orchestrate_stream()
        logger.debug("Preparing chunk workflow with stream targets: %r", stream_targets)
        chunk_workflow = self.workflow.to_chunk(sources=stream_targets)
        self._chunk_workflow = chunk_workflow
        return chunk_workflow

    # # Public methods ================================================================
    def orchestrate_stream(self) -> Mapping[StepKey, Any]:
        """Run or return the **stream phase**.

        This method runs the :py:attr:`orchestrator` on the stream workflow,
        and returns the produced stream targets.
        If the stream phase has already been computed, it returns the cached value.

        Returns:
            The stream targets produced by the orchestrator.
        """
        if self._stream_targets is not None:
            logger.info("Stream targets already computed.")
            logger.debug("Returning cached stream targets.")
            return self._stream_targets

        orchestrator = self.stream_orchestrator
        workflow = self.stream_workflow
        if orchestrator is None:
            if not workflow.empty:
                msg = (
                    "No stream orchestrator provided, "
                    "but the stream workflow is not empty."
                )
                raise RuntimeError(msg)

            logger.info("Stream workflow is empty, no orchestrator needed.")
            return collect_targets(workflow.graph, only_required=True)

        logger.info("Running stream phase with orchestrator %r.", orchestrator)
        stream_targets = orchestrator.run(self.stream_workflow)
        self._stream_targets = stream_targets
        return stream_targets

    def orchestrate_chunk(self, chunk_idx: int, /) -> Mapping[StepKey, Any]:
        """Run the **chunk phase** for ``chunk_idx``.

        1. Execute the **stream phase** if not already cached.
        2. Build the chunk workflow if not already cached.
        3. Executes the :py:attr:`orchestrator` on the selected chunk.

        Args:
            chunk_idx: 0-based index of the chunk to run.

        Returns:
            The result of running the orchestrator on the chunk graph.
        """
        chunk_workflow = self._prepare_chunk_workflow()
        chunk_orchestrator = self.chunk_orchestrator
        if chunk_orchestrator is None:
            msg = "No chunk orchestrator provided, cannot run chunk phase."
            raise RuntimeError(msg)

        logger.info(
            "Executing chunk %d with orchestrator %r.", chunk_idx, chunk_orchestrator
        )
        return chunk_orchestrator.run(chunk_workflow.select_chunk(chunk_idx))

    def schedule(self) -> Any:
        """Run the **chunk phase** for *all* chunks via the scheduler.

        1. Execute the **stream phase** if not already cached.
        2. Build the chunk workflow if not already cached.
        3. Calls the :py:attr:`scheduler` to run the orchestrator
           for each chunk in parallel.

        Returns:
            Backend-specific result of :py:meth:`SchedulerProtocol.run`.

        Raises:
            RuntimeError: If no scheduler has been provided.
        """
        chunk_workflow = self._prepare_chunk_workflow()

        scheduler = self.scheduler
        if scheduler is None:
            msg = "No scheduler provided, cannot run chunk phase."
            raise RuntimeError(msg)

        orchestrator = self.chunk_orchestrator
        if orchestrator is None:
            msg = "No chunk orchestrator provided, cannot run chunk phase."
            raise RuntimeError(msg)

        return scheduler.run(chunk_workflow, orchestrator)
