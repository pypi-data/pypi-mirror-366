"""Provides a debug orchestrator for inspecting a workflow without execution."""

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, Any, NoReturn

from pydantic import BaseModel, ConfigDict

from .._utils.debug import DebugHalt
from ..core._graph.base import n

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ..core.step import StepKey
    from ..core.workflow import RunnableWorkflow
    from ..registry._key import OrchestratorKey

__all__ = ["DebugOrchestrator"]

logger = getLogger(__name__)


def _halt() -> NoReturn:
    """Raise an :py:class:`digout._utils.debug.DebugHalt` exception.

    This is the intended mechanism for the debug orchestrator to prevent
    any further processing after it has displayed its information.
    """
    msg = "The debug orchestrator has finished to run."
    raise DebugHalt(msg)


class DebugOrchestrator(BaseModel):
    """A non-executing orchestrator for workflow inspection.

    Instead of running the steps, this orchestrator logs the planned execution
    order and which targets would be returned and then stops the execution
    by raising a :py:class:`~digout._utils.debug.DebugHalt` exception.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    def run(self, workflow: RunnableWorkflow[Any], /) -> Mapping[StepKey, object]:
        """Log the planned execution path and halts the workflow.

        This method calculates the topological order of steps to be run and logs
        them. It also logs which step outputs would be returned as final targets.
        It does not execute any steps and always concludes by raising a
        :py:class:`~digout._utils.debug.DebugHalt` exception to stop the entire
        process.

        Args:
            workflow: The workflow to inspect.

        Raises:
            DebugHalt: Always raised to terminate the workflow after logging.
        """
        from networkx import topological_sort  # noqa: PLC0415

        graph = workflow.graph
        ordered_step_keys = [
            step_key
            for step_key in topological_sort(graph)
            if "target" not in graph.nodes[step_key]
        ]

        if not ordered_step_keys:
            logger.info(
                "There are no steps to run: the orchestrator would not run anything."
            )
            _halt()

        logger.info(
            "The orchestrator would run the following steps in order: %s",
            ", ".join(repr(step_key) for step_key in ordered_step_keys),
        )

        target_keys = [
            step_key
            for step_key, attrs in graph.nodes(data=True)
            if n(attrs)["required"]
        ]
        if target_keys:
            logger.info(
                "The orchestrator would return the following targets: %s",
                ", ".join(repr(step_key) for step_key in target_keys),
            )
        else:
            logger.warning("No targets found in the workflow.")

        _halt()

    @classmethod
    def get_key(cls) -> OrchestratorKey:
        """Return the key for this orchestrator, ``debug``."""
        return "debug"
