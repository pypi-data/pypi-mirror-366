"""Provides an orchestrator that runs workflow steps sequentially."""

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, Any, TypeVar, cast

from pydantic import BaseModel, ConfigDict

from ..core._graph.base import collect_targets, n, replace_step_with_target

if TYPE_CHECKING:
    from collections.abc import Mapping

    from networkx import DiGraph

    from ..core._graph import NodeAttrs
    from ..core.step import StepKey, StepProtocol
    from ..core.workflow import RunnableWorkflow
    from ..registry import OrchestratorKey

__all__ = ["SimpleOrchestrator"]

logger = getLogger(__name__)

T = TypeVar("T", bound=Any)


def _get_step(attrs: NodeAttrs, step_key: StepKey) -> StepProtocol[Any, Any]:
    """Retrieve the step object from a node's attributes.

    Args:
        attrs: The attribute dictionary of the graph node.
        step_key: The identifier of the node, used for error messages.

    Returns:
        The step object stored in the node's attributes.

    Raises:
        RuntimeError: If the ``'step'`` key is not present in the attributes.
    """
    try:
        return attrs["step"]
    except KeyError as e:
        msg = f"Step key '{step_key}' does not have a step set."
        raise RuntimeError(msg) from e


def _get_target(attrs: NodeAttrs, step_key: StepKey) -> object | None:
    """Retrieve the target (output) from a node's attributes.

    Args:
        attrs: The attribute dictionary of the graph node.
        step_key: The identifier of the node, used for error messages.

    Returns:
        The target value produced by the step.

    Raises:
        RuntimeError: If the ``'target'`` key is not present in the attributes.
    """
    try:
        return attrs["target"]
    except KeyError as e:
        msg = f"Step key '{step_key}' does not have a target set."
        raise RuntimeError(msg) from e


def _get_sources(graph: DiGraph[StepKey], step_key: StepKey) -> dict[StepKey, Any]:
    """Gathers the outputs of a node's predecessors to use as its inputs.

    This function iterates over the direct predecessors of the node identified
    by ``step_key`` and collects their ``target`` values.

    Args:
        graph: The workflow graph.
        step_key: The identifier of the node for which to gather inputs.

    Returns:
        A dictionary mapping each predecessor's key to its target value.
    """
    return {
        predecessor_key: _get_target(n(graph.nodes[predecessor_key]), predecessor_key)
        for predecessor_key in graph.predecessors(step_key)
    }


class SimpleOrchestrator(BaseModel):
    """An orchestrator that runs workflow steps sequentially.

    This orchestrator executes the steps in the workflow one by one, following
    a topological sort of the dependency graph. This ensures that a step is
    only run after all of its prerequisites have been completed.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    def run(self, workflow: RunnableWorkflow[Any], /) -> Mapping[StepKey, object]:
        """Execute the workflow in a single sequence.

        The method first determines the execution order by performing a
        topological sort of the workflow graph. It then iterates through each
        step that has not yet been run, gathers the outputs from its
        predecessors, executes the step, and stores its output.

        Args:
            workflow: The workflow to execute.

        Returns:
            A mapping of step keys to their outputs for all steps that were
            marked as required in the workflow.
        """
        from networkx import topological_sort  # noqa: PLC0415

        graph = workflow.graph.copy()
        context = workflow.context

        # Find all steps to run
        ordered_step_keys = [
            step_key
            for step_key in topological_sort(graph)
            if "target" not in graph.nodes[step_key]
        ]

        if ordered_step_keys:
            logger.info("Running steps in order: %r", ordered_step_keys)
            for step_key in ordered_step_keys:
                logger.info("Running step: %r", step_key)

                attrs = cast("NodeAttrs", graph.nodes[step_key])
                step = _get_step(attrs, step_key)
                sources = _get_sources(graph, step_key)

                logger.debug("Sources for step %r: %s", step_key, sources)
                target = step.run(sources, context)
                logger.debug("Target for step %r: %s", step_key, target)
                replace_step_with_target(attrs, target)
            logger.info("All steps completed successfully.")
        else:
            logger.info("No steps to run.")

        # Collect and return the targets from all required nodes.
        return collect_targets(graph, only_required=True)

    @classmethod
    def get_key(cls) -> OrchestratorKey:
        """Return the orchestrator's registry key: ``simple``."""
        return "simple"
