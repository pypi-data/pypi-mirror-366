"""Split the general graph of steps into stream and chunk graphs."""

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, cast

from ..step import StepKey, StepKind
from .base import get_step_kind, n, replace_step_with_target

if TYPE_CHECKING:
    from collections.abc import Mapping

    from networkx import DiGraph

logger = getLogger(__name__)


def _get_required_stream_nodes_for_chunk_graph(
    graph: DiGraph[StepKey], /
) -> set[StepKey]:
    """Get the required stream nodes for the chunk graph.

    Args:
        graph: The overall directed acyclic graph (DAG) of steps, including
            both stream and chunk steps.

    Returns:
        A set of step keys that are required to be run in the chunk graph.
        These are the predecessors of chunk steps that are stream steps.
    """
    return {
        pred
        for pred, succ in graph.edges
        if (
            get_step_kind(graph.nodes[pred]) is StepKind.STREAM
            and get_step_kind(graph.nodes[succ]) is StepKind.CHUNK
        )
    }


def get_stream_graph(graph: DiGraph[StepKey]) -> DiGraph[StepKey]:
    """Get the stream graph from the given overall graph.

    Args:
        graph: The overall directed acyclic graph (DAG) of steps, including
            both stream and chunk steps.
            3 assumpations are made:
            - The graph is a valid DAG.
            - Chunk steps always follow stream steps, not the other way around.
            - Target nodes do not have any predecessors.

    Returns:
        A directed acyclic graph (DAG) containing only stream steps
        and their targets.
        The predecessors of chunk steps are marked as required, so that
        they are guaranteed to be run.
    """
    # 1. Find ALL stream nodes in the graph.
    stream_nodes = {
        node
        for node, attrs in graph.nodes(data=True)
        if get_step_kind(attrs) is StepKind.STREAM
    }

    # 2. Find ALL target nodes in the graph.
    #    They are considered as stream nodes as well.
    target_nodes = {node for node, attrs in graph.nodes(data=True) if "target" in attrs}

    nodes_in_stream_graph = stream_nodes.union(target_nodes)

    # 3. Subgraph the original graph to get the stream graph.
    logger.debug(
        "Creating stream graph with %d nodes: %s",
        len(nodes_in_stream_graph),
        nodes_in_stream_graph,
    )
    stream_graph = cast(
        "DiGraph[StepKey]", graph.subgraph(nodes_in_stream_graph).copy()
    )

    # 4. Mark the predecessors of chunk nodes as targets in the stream graph.
    #    This is necessary to ensure that the chunk graph can run later.
    chunk_predecessors = _get_required_stream_nodes_for_chunk_graph(graph)
    logger.debug(
        "Marking %d predecessors of chunk nodes as required in the stream graph: %s",
        len(chunk_predecessors),
        chunk_predecessors,
    )
    for node in chunk_predecessors:
        assert node in stream_graph  # sanity check
        n(stream_graph.nodes[node])["required"] = True

    return stream_graph


_unset = object()
"""A sentinel value to indicate that a value is not set."""


def get_chunk_graph(
    graph: DiGraph[StepKey], targets: Mapping[StepKey, object]
) -> DiGraph[StepKey]:
    """Get the chunk graph from the given overall graph.

    Args:
        graph: The overall directed acyclic graph (DAG) of steps, including
            both stream and chunk steps.
            3 assumpations are made:
            - The graph is a valid DAG.
            - Chunk steps always follow stream steps, not the other way around.
            - Target nodes do not have any predecessors.
        targets: Mapping of step keys to their target streams.
            This is the output of the stream graph, which is used to set the
            sources of the chunk graph.

    Returns:
        A directed acyclic graph (DAG) containing only chunk steps
        and their targets.
        The predecessors of stream steps are marked as targets, so that
        they are guaranteed to be run.

    Raises:
        RuntimeError: If a stream node in the chunk graph does not have a target
            provided through the ``targets`` argument.
    """
    targets = dict(targets)

    # 1. Find all chunk nodes in the graph.
    chunk_nodes = {
        node
        for node, attrs in graph.nodes(data=True)
        if get_step_kind(attrs) is StepKind.CHUNK
    }

    # 2. Find the predecessors of the chunk nodes.
    #    They should either be stream nodes, or target nodes.
    #    Either way, they need to be included in the chunk graph.
    chunk_predecessors = set[StepKey]().union(
        *(graph.predecessors(node) for node in chunk_nodes)
    )

    # 3. Subgraph the original graph to get the chunk graph.
    nodes_in_chunk_graph = chunk_nodes.union(chunk_predecessors)
    logger.debug(
        "Creating chunk graph with %d nodes: %s",
        len(nodes_in_chunk_graph),
        nodes_in_chunk_graph,
    )
    chunk_graph = cast("DiGraph[StepKey]", graph.subgraph(nodes_in_chunk_graph).copy())

    # 4. Replace the remaining stream nodes with their targets.
    for node, attrs in chunk_graph.nodes(data=True):
        if get_step_kind(attrs) is StepKind.STREAM:
            if (target := targets.pop(node, _unset)) is not _unset:
                logger.debug(
                    "Replacing stream node %r with target %r in chunk graph.",
                    node,
                    target,
                )
                replace_step_with_target(n(attrs), target)
            else:
                msg = f"No target found for stream node {node!r} in chunk graph."
                raise RuntimeError(msg)

    if targets:
        logger.debug(
            "The following targets were not used in the chunk graph: %s",
            targets.keys(),
        )

    return chunk_graph
