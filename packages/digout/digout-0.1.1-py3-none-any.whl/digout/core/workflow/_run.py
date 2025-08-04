"""A workflow that can be run.

There are two types of runnable workflows:
- A stream workflow: sources are streams, steps are stream-like.
- A chunk workflow: sources are chunks, steps are chunk-like.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

from .._graph import reduce_graph_to_runtime
from ._base import C, WorkflowBase

if TYPE_CHECKING:
    from networkx import DiGraph

    from ..step import StepKey, StepKind


@dataclass(frozen=True)
class RunnableWorkflow(WorkflowBase[C]):
    """A workflow that can be run.

    It includes a graph of steps and targets, and the context to run the steps.
    This is the object passed to the
    :py:class:`digout.core.orchestrator.OrchestratorProtocol` orchestrator
    to run the workflow.
    """

    kind: StepKind
    """The kind of steps in the workflow."""

    def reduce(self) -> Self:
        """Reduce the graph to only includes steps that need to be run.

        Steps that have already been run are removed from the graph.

        Returns:
            A new instance of the workflow with the reduced graph.
        """
        graph: DiGraph[StepKey] = reduce_graph_to_runtime(self.graph, self.context)
        return self.__class__(graph=graph, context=self.context, kind=self.kind)

    @property
    def empty(self) -> bool:
        """Check if the workflow is empty.

        An empty workflow has no step nodes.
        """
        return not {
            step_key
            for step_key, attrs in self.graph.nodes(data=True)
            if "step" in attrs
        }
