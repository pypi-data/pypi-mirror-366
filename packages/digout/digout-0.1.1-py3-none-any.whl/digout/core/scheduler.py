"""Interface for a **scheduler**, the component that executes *chunk workflows*.

A scheduler receives a :py:class:`~digout.core.workflow.ChunkWorkflow`, splits it
into one runnable workflow per chunk, and delegates each of those workflows to
an :py:class:`~digout.core.orchestrator.OrchestratorProtocol` instance.  It does
*not* run step logic itself; that remains the orchestrator's job.
"""

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from .orchestrator import OrchestratorProtocol
    from .workflow import ChunkWorkflow


__all__ = ["SchedulerProtocol"]

logger = getLogger(__name__)


@runtime_checkable
class SchedulerProtocol(Protocol):
    """Interface every concrete scheduler must implement.

    The scheduler distributes chunk execution: for each chunk of the input
    :py:class:`~digout.core.workflow.ChunkWorkflow` it calls
    :py:meth:`digout.core.orchestrator.OrchestratorProtocol.run` on a runnable
    workflow derived from that chunk.
    """

    def run(
        self, workflow: ChunkWorkflow[Any, Any], orchestrator: OrchestratorProtocol, /
    ) -> Any:
        """Run the orchestrator once for every chunk in ``workflow``.

        The targets stored in a :py:class:`~digout.core.workflow.ChunkWorkflow`
        are still streams; they must be split into individual chunks via
        :py:meth:`~digout.core.workflow.ChunkWorkflow.select_chunk`.  For each
        chunk this method builds the runnable workflow and passes it to
        ``orchestrator``.

        Args:
            workflow: The chunk workflow to process.
            orchestrator: Object that executes the runnable workflow for a
                single chunk.

        Returns:
            Backend-specific result object.
        """
        ...
