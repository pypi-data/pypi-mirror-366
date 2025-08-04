"""Interfaces for a **step**, the atomic unit of work in a DIGOUT workflow.

A step consumes one or more **source** objects (produced by its dependencies)
and emits a single **target** object.

Two kinds of steps exist:

* **Stream step**: runs once during the *stream phase* and can return any
  object, including another stream.  If the result is a stream it will later
  be partitioned into chunks processed by chunk steps.
* **Chunk step**: runs once per chunk during the *chunk phase* and processes
  exactly one chunk at a time.
"""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, Protocol, TypeAlias, TypeVar, runtime_checkable

if TYPE_CHECKING:
    from collections.abc import Mapping


__all__ = ["NotRunError", "StepKey", "StepKind", "StepProtocol"]


T_co = TypeVar("T_co", covariant=True)
"""Type of a *target* object produced by the step."""

C_contra = TypeVar("C_contra", contravariant=True)
"""Context type variable for the step protocol."""

StepKey: TypeAlias = str
"""Alias for the step key type, which is a string.

A step key uniquely identifies a step within a workflow.
It is used:

- in the :py:meth:`StepProtocol.get_source_keys` method to declare dependencies,
- as names of the nodes in the workflow graph.
"""


class StepKind(StrEnum):
    """Kind of a :class:`StepProtocol` (read via :py:attr:`StepProtocol.kind`)."""

    STREAM = "stream"
    """Runs once for the whole stream during the *stream phase*.

    Usually returns a :class:`digout.core.stream.StreamProtocol`, but may also
    return any other object.
    """

    CHUNK = "chunk"
    """Runs once per chunk during the *chunk phase*."""


class NotRunError(Exception):
    """Raised when a step's target is requested but the step never ran."""


@runtime_checkable
class StepProtocol(Protocol[C_contra, T_co]):
    """Interface every concrete step must implement.

    * Declare upstream dependencies with :py:meth:`get_source_keys`.
    * Perform the work in :py:meth:`run`.
    * Indicate whether it has already produced its target via
      :py:meth:`has_run` (so dependencies can be skipped).
    * Provide the previously produced target with :py:meth:`get_target`.

    Notes:
        It is assumed that the *context* alone is sufficient
        to decide whether the step has run and to retrieve its target.
    """

    def get_source_keys(self) -> set[StepKey]:
        """Return the step keys this step depends on."""
        ...

    def run(self, sources: Mapping[str, object], context: C_contra, /) -> T_co:
        """Execute the step.

        Args:
            sources: Mapping from upstream step key to the object it produced.
                Keys must match :py:meth:`get_source_keys`.
            context: Workflow context.  Identical for every step within the
                stream graph (stream phase) *or* for every step of a given
                chunk graph (chunk phase).

        Returns:
            The **target** object created by this step.
        """
        ...

    def has_run(self, context: C_contra, /) -> bool:
        """Return ``True`` if this step has already produced its target."""
        ...

    def get_target(self, context: C_contra, /) -> T_co:
        """Return the previously produced target.

        Raises:
            NotRunError: If no target is available (i.e. the step has not run).
        """
        ...

    @property
    def kind(self) -> StepKind:
        """Either :py:attr:`StepKind.STREAM` or :py:attr:`StepKind.CHUNK`."""
        ...
