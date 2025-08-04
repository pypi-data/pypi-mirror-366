"""Context interface for DIGOUT workflows.

When a :py:class:`~digout.core.workflow.RunnableWorkflow` executes, the same
**context** instance is passed to every step.  The context stores information
that must be shared across several steps during one workflow run.
"""

from __future__ import annotations

from typing import Protocol, Self

__all__ = ["ContextProtocol"]


class ContextProtocol(Protocol):
    """Interface every concrete context must implement.

    A context exists in two flavours:

    * **Stream context**: shared by every *stream step* during the stream
      phase.
    * **Chunk context**: one instance *per chunk*, shared by every chunk step
      that works on that chunk during the chunk phase.

    The chunk context is built in the following way:

    1. Each stream converts the *stream context* into a *chunk context* via
       :py:meth:`digout.core.stream.StreamProtocol.get_chunk_context`.
    2. If multiple streams contribute a chunk context, the individual contexts
       are merged with :py:meth:`combine`.
    """

    def combine(self, *others: Self) -> Self:
        """Merge ``self`` with ``others`` and return the combined context."""
        ...
