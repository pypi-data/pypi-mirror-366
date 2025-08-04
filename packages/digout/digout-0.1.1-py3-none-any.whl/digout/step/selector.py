"""Define a Pydantic model for selecting a subset of items from a sequence.

This module provides Pydantic models that represent different strategies for
filtering a sequence:

- :py:class:`RangeSelector`: Selects a range of items based on start and end indices.
- :py:class:`IndicesSelector`: Selects items based on a list of specific indices.

These are used to select a subset of files for creating a moore stream
in :py:mod:`digout.step.createmoorestream`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Literal, TypeVar

from pydantic import BaseModel, Discriminator, Field

if TYPE_CHECKING:
    from collections.abc import Sequence

__all__ = ["IndicesSelector", "RangeSelector", "Selector"]

T = TypeVar("T")


class RangeSelector(BaseModel):
    """A selector that extracts a contiguous slice from a sequence."""

    type: Literal["range"] = "range"
    """The type discriminator, used for parsing."""

    start_idx: Annotated[int, Field(ge=0)] = 0
    """The starting index of the slice (inclusive)."""

    end_idx: int | None = None
    """The ending index of the slice (exclusive).

    If ``None``, the slice extends to the end of the sequence.
    """

    def select(self, sequence: Sequence[T]) -> list[T]:
        """Select a sub-sequence using the defined start and end indices.

        Args:
            sequence: The input sequence from which to select items.

        Returns:
            A new list containing the selected items.

        Raises:
            IndexError: If ``start_idx`` is out of bounds for the sequence.
        """
        if self.start_idx > len(sequence):
            msg = (
                f"Start index {self.start_idx} is out of bounds "
                f"for the sequence of length {len(sequence)}."
            )
            raise IndexError(msg)

        if self.end_idx is None:
            output = sequence[self.start_idx :]
        output = sequence[self.start_idx : self.end_idx]

        if not isinstance(output, list):
            output = list(output)

        return output


class IndicesSelector(BaseModel):
    """A selector that cherry-picks items from a sequence by their indices."""

    type: Literal["indices"] = "indices"
    """The type discriminator, used for parsing."""

    indices: list[int] | None = None
    """A list of integer indices specifying which items to select."""

    def select(self, sequence: Sequence[T]) -> list[T]:
        """Select items from the sequence corresponding to the given indices.

        Args:
            sequence: The input sequence from which to select items.

        Returns:
            A new list containing the selected items in the order specified
            by the `indices` list.
        """
        if self.indices is None:
            if not isinstance(sequence, list):
                sequence = list(sequence)
            return sequence

        return [sequence[idx] for idx in self.indices]


Selector = Annotated[RangeSelector | IndicesSelector, Discriminator("type")]
"""A discriminated union of all available selector types.

Pydantic uses the ``type`` field to automatically determine whether to parse
the input data as a :py:class:`RangeSelector` or an :py:class:`IndicesSelector`.
"""
