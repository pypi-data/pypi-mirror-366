"""Common interface shared by all workflow types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from networkx import DiGraph

    from ..context import ContextProtocol
    from ..step import StepKey


C = TypeVar("C", bound="ContextProtocol")
"""Type variable for the context type of the workflow."""


@dataclass(frozen=True)
class WorkflowBase(Generic[C]):
    """Base class for any workflow.

    Exposes two public attributes:

    * **graph**: a ``networkx.DiGraph`` DAG of steps and data.
    * **context**: the context object passed to every step.
    """

    graph: DiGraph[StepKey]
    """Directed-acyclic graph (DAG) of steps and data.

    A node has the following attributes:

    * ``step`` *(optional)*: a :py:class:`digout.core.step.StepProtocol`
      instance to run.
    * ``target`` *(optional)*: pre-computed data used as a source.
    * ``required``: ``True`` if the node must be produced for the workflow
      to be complete.

    A node sets **either** ``step`` **or** ``target``, not both.

    Edges encode the dependencies declared by
    :py:meth:`digout.core.step.StepProtocol.get_source_keys`.
    """

    context: C
    """Context object.

    It is supplied to each step's
    :py:meth:`~digout.core.step.StepProtocol.run` method.
    and :py:meth:`~digout.core.step.StepProtocol.has_run` method.
  """
