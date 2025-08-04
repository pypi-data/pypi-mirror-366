"""Generic workflow containing both stream and chunk steps."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Generic, Self, TypeVar

from .._graph import build_graph, get_chunk_graph, get_stream_graph
from ..step import StepKind
from ._base import WorkflowBase
from ._chunk import ChunkWorkflow
from ._run import RunnableWorkflow

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ..context import ContextProtocol
    from ..step import StepKey, StepProtocol

C_stream = TypeVar("C_stream", bound="ContextProtocol")
"""Type variable for the context type of stream steps."""

C_chunk = TypeVar("C_chunk", bound="ContextProtocol")
"""Type variable for the context type of chunk steps."""


@dataclass(frozen=True)
class GenericWorkflow(WorkflowBase[C_stream], Generic[C_stream, C_chunk]):
    """A mixed workflow of stream + chunk steps.

    Convert to

    * a **stream workflow** with :py:meth:`to_stream`;
    * a **chunk workflow** with :py:meth:`to_chunk`.
    """

    @classmethod
    def from_steps(
        cls,
        steps: Mapping[StepKey, StepProtocol[Any, Any]],
        required_keys: set[StepKey],
        sources: Mapping[StepKey, object],
        context: C_stream,
    ) -> Self:
        """Build a workflow from steps.

        Starting from the ``required_keys``, iteratively add each step's upstream
        dependencies (see :py:meth:`digout.core.step.StepProtocol.get_source_keys`)
        unless the step's target is supplied in *sources*.

        Args:
            steps: Mapping of keys to step instances.
            required_keys: Keys that must appear in the resulting DAG.
            sources: Pre-computed targets keyed by step.
            context: Stream-phase context.

        Returns:
            A :py::class:`GenericWorkflow` with the constructed graph and *context*.
        """
        graph = build_graph(steps=steps, required_keys=required_keys, sources=sources)
        return cls(graph=graph, context=context)

    def to_stream(self, *, reduce: bool = True) -> RunnableWorkflow[C_stream]:
        """Return a runnable **stream workflow**.

        The graph keeps:

        * all stream steps;
        * every target object (considered stream-like).

        Immediate predecessors of chunk steps are marked *required* so the
        subsequent chunk phase can run.

        If ``reduce`` is ``True`` (default) the graph is trimmed to the minimal
        set of steps needed for the required targets.
        """
        graph = get_stream_graph(self.graph)
        workflow = RunnableWorkflow(
            graph=graph, context=self.context, kind=StepKind.STREAM
        )
        if reduce:
            workflow = workflow.reduce()

        return workflow

    def to_chunk(
        self, sources: Mapping[StepKey, object]
    ) -> ChunkWorkflow[C_stream, C_chunk]:
        """Return a **chunk workflow**.

        The chunk graph contains all chunk steps plus their stream-like sources.
        Provide those sources via ``sources``, typically the outputs produced by
        the stream phase.

        Raises:
            RuntimeError: If a stream node in the chunk graph lacks a target in
                ``sources``.
        """
        graph = get_chunk_graph(self.graph, targets=sources)
        return ChunkWorkflow(graph=graph, context=self.context)
