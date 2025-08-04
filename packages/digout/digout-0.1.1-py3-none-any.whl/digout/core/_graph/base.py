"""Base classes to define a graph of steps.

The expected node attributes are defined as a :py:class:`NodeAttrs` typed dictionary.
Other utilities are provided to manipulate the node attributes.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, NotRequired, TypedDict, cast

if TYPE_CHECKING:
    from collections.abc import Mapping

    from networkx import DiGraph

    from ..step import StepKey, StepKind, StepProtocol

_unset = object()
"""A sentinel value to indicate that a key is not set in a dictionary."""


class NodeAttrs(TypedDict):
    """Attributes of a node in the DAG.

    This is used to store additional information about each step in the DAG.
    """

    step: NotRequired[StepProtocol[Any, Any]]
    """The step configuration associated with this node."""

    required: bool
    """Whether the step is a required step in the workflow."""

    target: NotRequired[object]
    """The target output of the step, if applicable.

    The target should be a stream for a generic or stream graph,
    and a chunk for a chunk graph.
    """


def n(attrs: Mapping[str, Any]) -> NodeAttrs:
    """Type cast the given attributes to NodeAttrs."""
    return cast("NodeAttrs", attrs)


def get_step_kind(attrs: Mapping[str, Any]) -> StepKind | None:
    """Get the step kind from the node attributes."""
    step = n(attrs).get("step")
    return step.kind if step is not None else None


def replace_step_with_target(node_attrs: NodeAttrs, target: object) -> None:
    """Replace the step in the node attributes with the target.

    The step is removed from the attributes, and the target is set.

    Args:
        node_attrs: The attributes of the node to modify.
        target: The target to set in the node attributes.
    """
    node_attrs.pop("step")
    assert "target" not in node_attrs
    node_attrs["target"] = target


def collect_targets(
    graph: DiGraph[StepKey], *, only_required: bool = False
) -> dict[str, object]:
    """Get the targets from the node attributes.

    This returns a dictionary of step keys to their target outputs.

    Args:
        graph: The workflow graph.
        only_required: If ``True``, only include targets of required steps.

    Returns:
        A dictionary mapping step keys to their target outputs.
    """
    return {
        key: target
        for key, attrs in graph.nodes(data=True)
        if (target := n(attrs).get("target"), _unset) is not _unset
        and (not only_required or n(attrs)["required"])
    }
