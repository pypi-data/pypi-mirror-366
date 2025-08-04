from __future__ import annotations

from typing import TYPE_CHECKING

from .._graph.base import get_step_kind
from ..step import StepKey, StepKind

if TYPE_CHECKING:
    from networkx import DiGraph


def validate_graph(graph: DiGraph[StepKey]) -> None:
    """Raise an exception if *dag* is ill-formed.

    Checks the following assumptions:
    1. The graph must be a true directed **acyclic** graph.
    2. Edges may **not** point from a chunk-level step to a stream-level step.
    3. A node has either a step, or its target, but not both.
    4. Target nodes do not have any predecessors.
    """
    from networkx import is_directed_acyclic_graph  # noqa: PLC0415

    # 1. Check if the graph is a valid DAG.
    if not is_directed_acyclic_graph(graph):
        msg = "The graph is not a valid directed acyclic graph (DAG)."
        raise ValueError(msg)

    # 2. Check that edges do not point from chunk to stream steps.
    for predecessor, successor in graph.edges:
        # can only have [kind=StepKind.STREAM] -> [kind=StepKind.CHUNK|STREAM]
        predecessor_kind = get_step_kind(graph.nodes[predecessor])
        successor_kind = get_step_kind(graph.nodes[successor])
        if predecessor_kind is StepKind.CHUNK and successor_kind is StepKind.STREAM:
            msg = (
                f"Step {predecessor!r} with '{predecessor_kind!s}' kind cannot "
                f"depend on step {successor!r} with '{successor_kind!s}' kind. "
                "Chunk steps cannot depend on stream steps."
            )
            raise ValueError(msg)

    # 3. Check that nodes have either a step or a target, but not both.
    for node, attrs in graph.nodes(data=True):
        if "step" in attrs and "target" in attrs:
            msg = (
                f"Node {node!r} has both 'step' and 'target' attributes. "
                "A node can have either a step or a target, but not both."
            )
            raise ValueError(msg)

    # 4. Check that target nodes do not have any predecessors.
    for node, attrs in graph.nodes(data=True):
        if "target" in attrs and graph.in_degree[node] > 0:
            msg = (
                f"Node {node!r} is a target node, but has predecessors. "
                "Target nodes should not have any predecessors."
            )
            raise ValueError(msg)
