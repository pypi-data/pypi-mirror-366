"""Interfaces and helpers for working with **streams** of data chunks.

A *stream* models a dataset that can be partitioned into independent *chunks*
so the **DIGOUT** workflow can process those chunks in parallel.
"""

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, Any, Protocol, TypeVar, runtime_checkable

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    from ..core.context import ContextProtocol
    from ..core.step import StepKey

__all__ = ["StreamProtocol", "get_context_for_chunk", "get_n_chunks"]

T_co = TypeVar("T_co", covariant=True)
"""Type of a single chunk inside a stream."""


logger = getLogger(__name__)

C_stream_contra = TypeVar(
    "C_stream_contra", bound="ContextProtocol", contravariant=True
)
"""Input context type variable for the stream protocol."""

C_chunk_co = TypeVar("C_chunk_co", bound="ContextProtocol", covariant=True)
"""Output context type variable for the stream protocol."""


@runtime_checkable
class StreamProtocol(Protocol[T_co, C_stream_contra, C_chunk_co]):
    """Interface every concrete stream must implement.

    A **stream** is an ordered collection of chunks.  Each chunk can be processed
    independently in the **chunk phase**, enabling parallel execution.

    * Provide the total number of chunks via :py:attr:`n_chunks`.
    * Return an individual chunk via :py:meth:`get_chunk`.
    * Derive the per-chunk context via :py:meth:`get_chunk_context`.  The method
      receives the *stream-phase* context and may transform or enrich it for
      the chunk.
    """

    @property
    def n_chunks(self) -> int:
        """Total number of chunks (`> 0`)."""
        ...

    def get_chunk(self, index: int, /) -> T_co:
        """Return the chunk located at ``index``.

        Args:
            index: Zero-based index of the desired chunk.

        Raises:
            IndexError: If ``index`` is outside ``[0, n_chunks)``.
        """
        ...

    def get_chunk_context(
        self, index: int, context: C_stream_contra
    ) -> C_chunk_co | None:
        """Return the context object for the chunk at ``index``.

        Args:
            index: Zero-based chunk index.
            context: Context instance that was used during the stream phase.

        Returns:
            A context instance specific to the chunk, or ``None`` if the
            stream does not supply one.
        """
        ...


def get_n_chunks(streams: Iterable[StreamProtocol[Any, Any, Any]], /) -> int:
    """Return the common number of chunks shared by all ``streams``.

    All streams participating in one workflow must expose the same number of
    chunks. This helper validates the constraint and returns that number.

    Args:
        streams: Iterable of streams to inspect.

    Raises:
        ValueError: If ``streams`` is empty or if the streams expose different
            numbers of chunks.
    """
    lengths = {stream.n_chunks for stream in streams}
    if not lengths:
        msg = "No streams provided."
        raise ValueError(msg)

    if len(lengths) != 1:
        msg = (
            "All streams must have the same number of chunks. "
            "Found lengths: " + ", ".join(map(str, lengths)) + "."
        )
        raise ValueError(msg)

    return lengths.pop()


C_stream = TypeVar("C_stream", bound="ContextProtocol")
C_chunk = TypeVar("C_chunk", bound="ContextProtocol")


def get_context_for_chunk(
    context: C_stream,
    streams: Mapping[StepKey, StreamProtocol[Any, C_stream, C_chunk]],
    chunk_idx: int,
) -> C_chunk:
    """Build the context for ``chunk_idx`` by combining per-stream contexts.

    Each stream may return a context for a given chunk via
    :py:meth:`StreamProtocol.get_chunk_context`.  The contexts returned by all
    streams are combined using :py:meth:`~digout.core.context.ContextProtocol.combine`.

    Args:
        context: Context object from the stream phase.
        streams: Mapping from step key to stream.
        chunk_idx: Zero-based index of the chunk.

    Returns:
        The context object to pass to chunk steps.

    Raises:
        RuntimeError: If no stream provides a context for the requested chunk.
    """
    contexts: list[C_chunk] = [
        output_context
        for stream in streams.values()
        if (output_context := stream.get_chunk_context(chunk_idx, context)) is not None
    ]
    if not contexts:
        msg = (
            f"None of the streams provided a context for chunk {chunk_idx}. "
            "Streams: " + ", ".join(map(repr, streams.keys())) + "."
        )
        raise RuntimeError(msg)

    return contexts[0].combine(*contexts[1:])
