"""Interface for an **orchestrator**, the component that *executes* a workflow.

A concrete orchestrator receives a
:py:class:`~digout.core.workflow.RunnableWorkflow`, walks its directed-acyclic
graph in dependency order, and calls
:py:meth:`digout.core.step.StepProtocol.run` on each step.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from collections.abc import Mapping

    from .step import StepKey
    from .workflow import RunnableWorkflow

__all__ = ["OrchestratorProtocol"]


@runtime_checkable
class OrchestratorProtocol(Protocol):
    """Interface every concrete orchestrator must implement."""

    def run(self, workflow: RunnableWorkflow[Any], /) -> Mapping[StepKey, object]:
        """Execute a runnable ``workflow`` and return the required targets.

        Args:
            workflow: The runnable workflow containing the DAG of **steps**
                and **targets**, and the **context** to pass to each step.

        Returns:
            Mapping from *step key* to the object (target) produced by the step.
            Only required keys may be returned.
        """
        ...
