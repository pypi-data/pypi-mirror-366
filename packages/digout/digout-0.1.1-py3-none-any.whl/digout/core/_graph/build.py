"""Build the graph of steps and targets."""

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, Any

from .base import NodeAttrs
from .validate import validate_graph

if TYPE_CHECKING:
    from collections.abc import Mapping, MutableMapping

    from networkx import DiGraph

    from ..step import StepKey, StepProtocol

_unset = object()
"""A sentinel value to indicate that a value is not set."""

logger = getLogger(__name__)


def _add_node(
    graph: DiGraph[StepKey],
    key: StepKey,
    steps: MutableMapping[StepKey, StepProtocol[Any, Any]],
    sources: MutableMapping[StepKey, object],
    required_step_keys: set[StepKey],
) -> StepProtocol[Any, Any] | None:
    """Add a node to the graph with the given key and attributes.

    Args:
        graph: The directed acyclic graph (DAG) to which the node will be added.
        key: The key of the step to be added.
        steps: Mapping of step keys to their step configurations.
        sources: Mapping of step keys to their target outputs.
        required_step_keys: Set of step keys that are required to run.

    Returns:
        The step configuration associated with the added node, or None if the node
        is a target.
        This allows to continue populating the graph with other nodes.
    """
    required = key in required_step_keys

    step: StepProtocol[Any, Any] | None
    node_attrs: NodeAttrs
    if (source := sources.pop(key, _unset)) is not _unset:
        logger.debug(
            "Adding node %r as a %starget.", key, "required " if required else ""
        )
        node_attrs = NodeAttrs(target=source, required=required)
        step = None
    else:
        logger.debug(
            "Adding node %r as a %sstep.", key, "required " if required else ""
        )
        try:
            step = steps.pop(key)
        except KeyError as e:
            msg = f"Step {key!r} was neither provided as a source nor as a step."
            raise ValueError(msg) from e
        node_attrs = NodeAttrs(step=step, required=required)

    graph.add_node(key, **node_attrs)
    return step  # None if the node is a target, otherwise the step configuration.


def build_graph(
    steps: Mapping[StepKey, StepProtocol[Any, Any]],
    required_keys: set[StepKey],
    sources: Mapping[StepKey, object],
    *,
    validate: bool = True,
) -> DiGraph[StepKey]:
    """Build a directed acyclic graph (DAG) from the given steps and required keys.

    The function starts from the required keys and traverses their dependencies,
    adding nodes and edges to the graph.

    Args:
        steps: Mapping of step keys to their step configurations.
        required_keys: Set of step keys that are required to run.
        sources: Mapping of step keys to their target outputs.
        validate: Whether to validate the DAG after building it.

    Returns:
        A directed acyclic graph (DAG) representing the workflow.
    """
    from networkx import DiGraph  # noqa: PLC0415

    if not required_keys:
        msg = (
            "No required keys provided. The graph cannot be built without "
            "required step keys."
        )
        raise ValueError(msg)

    # We'll pop those as we go, to check which steps/sources are not used.
    steps = dict(steps)
    sources = dict(sources)

    graph: DiGraph[StepKey] = DiGraph()

    stack: set[StepKey] = set(required_keys)
    visited: set[StepKey] = set()
    edges_to_add: set[tuple[StepKey, StepKey]] = set()
    while stack:
        key = stack.pop()
        visited.add(key)
        step = _add_node(
            graph=graph,
            key=key,
            steps=steps,
            sources=sources,
            required_step_keys=required_keys,
        )
        if step is not None:
            # Populate stack
            predecessors = step.get_source_keys()
            stack.update(predecessors - visited)
            # add edges to the graph
            edges_to_add.update((pred, key) for pred in predecessors)

    # Add edges to the graph
    logger.debug("Adding %d edges to the graph: %s", len(edges_to_add), edges_to_add)
    graph.add_edges_from(edges_to_add)

    if sources:  # warning
        logger.warning(
            "The following sources were not used in the graph: %s",
            ", ".join(map(repr, sources.keys())),
        )

    if steps:  # just an info
        logger.info(
            "The following steps were not used in the graph: %s",
            ", ".join(map(repr, steps.keys())),
        )

    # Validate the graph if requested
    if validate:
        validate_graph(graph)

    return graph
