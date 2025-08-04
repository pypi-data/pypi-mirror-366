"""Reduce the graph of steps to only the necessary steps that need to run."""

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, TypeVar, cast

from .base import n, replace_step_with_target

if TYPE_CHECKING:
    from networkx import DiGraph

    from ..context import ContextProtocol
    from ..step import StepKey

logger = getLogger(__name__)

N = TypeVar("N")


def _get_ancestors_with_self(graph: DiGraph[N], nodes: set[N]) -> set[N]:
    """Get the ancestors of the given nodes in the graph, including themselves.

    Args:
        graph: a graph.
        nodes: a set of nodes to find ancestors for.

    Returns:
        A set of nodes that includes the ancestors of the given nodes,
        as well as the nodes themselves.
    """
    from networkx import ancestors  # noqa: PLC0415

    return (
        set[N]().union(*(ancestors(graph, node) | {node} for node in nodes))
        if nodes
        else set[N]()
    )


def reduce_graph_to_runtime(
    graph: DiGraph[StepKey], context: ContextProtocol
) -> DiGraph[StepKey]:
    """Reduce the graph to only the steps that need to run.

    The function replaces nodes that have already run with their targets,
    removing their dependencies from the graph.
    Dependencies marked as targets cannot be removed, since their targets
    is required.

    Args:
        graph: The stream graph or the chunk graph to reduce.
        context: stream/chunk context used by the steps that are part of the graph.

    Returns:
        The reduced graph with only the necessary steps and targets.
    """
    # 1. Find the nodes that have already run.
    #    Replace them with their targets, and disconnect them from the graph.
    graph = graph.copy(as_view=False)
    node_was_deleted: bool = False
    edges_to_remove: set[tuple[StepKey, StepKey]] = set()
    for node, attrs_ in graph.nodes(data=True):
        attrs = n(attrs_)
        step = attrs.get("step")
        if step is not None and step.has_run(context):
            node_was_deleted = True
            logger.debug("Node %s has already run, replacing with target.", node)
            replace_step_with_target(attrs, step.get_target(context))
            edges_to_remove.update(graph.in_edges(node))

    if not node_was_deleted:
        logger.debug("No nodes have already run, can't reduce the graph.")
        return graph

    logger.debug(
        "Removing %d edges from nodes that have already run: %s",
        len(edges_to_remove),
        edges_to_remove,
    )
    graph.remove_edges_from(edges_to_remove)

    # 2. Only keep nodes that leads to a required node.
    #    This is done by finding the ancestors of the target nodes.
    target_nodes = {
        node for node, attrs in graph.nodes(data=True) if n(attrs)["required"]
    }
    needed_nodes = _get_ancestors_with_self(graph, target_nodes)
    logger.debug("Reducing graph to %d nodes: %s", len(needed_nodes), needed_nodes)
    return cast("DiGraph[StepKey]", graph.subgraph(needed_nodes).copy())
