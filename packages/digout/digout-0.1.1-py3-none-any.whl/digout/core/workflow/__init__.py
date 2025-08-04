"""Workflow building and conversion.

All workflow classes derive from :py:class:`WorkflowBase`, which stores

- :py:attr:`~WorkflowBase.graph`: a ``networkx.DiGraph`` DAG of steps and targets.
- :py:attr:`~WorkflowBase.context`: a :py:class:`~digout.core.context.ContextProtocol`
  instance passed to every step during execution.

Hierarchy
---------

* :py:class:`GenericWorkflow`: initial DAG containing both
  :py:class:`~digout.core.step.StepKind.STREAM` **and**
  :py:class:`~digout.core.step.StepKind.CHUNK` steps; **not runnable**.

* :py:class:`RunnableWorkflow`: any workflow an orchestrator can execute.
  Two variants exist:

  * **Stream workflow**: contains only stream steps/targets. Exactly one
    per :py:class:`GenericWorkflow`.
  * **Chunk workflow**: contains only chunk steps/targets. One per chunk of
    the stream(s).

* :py:class:`ChunkWorkflow`: helper that groups all chunk steps and exposes
  :py:meth:`ChunkWorkflow.select_chunk` to obtain a
  :py:class:`RunnableWorkflow` for a specific chunk.


The generic workflow can be converted into a

- a stream workflow using the :py:meth:`GenericWorkflow.to_stream` method,
  run once during the stream phase.
- a :py:class:`ChunkWorkflow` using the :py:meth:`GenericWorkflow.to_chunk` method,
  run once per chunk during the chunk phase.


Execution
---------

- An orchestrator (see
  :py:class:`~digout.core.orchestrator.OrchestratorProtocol`) walks any
  :py:class:`RunnableWorkflow` in topological order and runs each step while
  respecting dependencies.
- A scheduler (see
  :py:class:`~digout.core.scheduler.SchedulerProtocol`) can
  dispatch the many per-chunk workflows produced from a
  :py:class:`ChunkWorkflow` to the orchestrator in parallel.
"""

from __future__ import annotations

from ._base import WorkflowBase
from ._chunk import ChunkWorkflow
from ._generic import GenericWorkflow
from ._run import RunnableWorkflow

__all__ = [  # noqa: RUF022
    "WorkflowBase",
    "GenericWorkflow",
    "ChunkWorkflow",
    "RunnableWorkflow",
]
