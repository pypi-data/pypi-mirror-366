"""Define a protocol for discovering the chunk type of a stream."""

from __future__ import annotations

from typing import Protocol, TypeVar, runtime_checkable

__all__ = ["WithChunkTypeProtocol"]

T_co = TypeVar("T_co", covariant=True)
"""A covariant type variable representing the type of a chunk object."""


@runtime_checkable
class WithChunkTypeProtocol(Protocol[T_co]):
    """An interface for classes that can report their associated chunk type.

    This protocol provides a standard way for a class
    (typically a :py:class:`~digout.core.stream.StreamProtocol` subclass)
    to advertise the type of the chunks it generates.

    This allows to automatically discover chunk types, for populating
    the chunk registry for example.
    """

    @classmethod
    def get_chunk_type(cls) -> type[T_co]:
        """Return the type of the chunk object produced by this class."""
        ...
