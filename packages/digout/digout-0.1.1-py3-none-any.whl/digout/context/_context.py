"""Provides a :py:class:`~digout.core.context.ContextProtocol` implementation.

This module defines the :py:class:`Context` class, which is a Pydantic model used to
pass shared state, component registries and dynamic placeholders,
throughout the different steps of a DIGOUT workflow.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Self, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from ..registry import Registries

if TYPE_CHECKING:
    from collections.abc import Mapping

__all__ = ["Context"]

K = TypeVar("K")
V = TypeVar("V")


def _safely_combine_dictionaries(*dicts: Mapping[K, V]) -> dict[K, V]:
    """Combine multiple dictionaries, raising an error on key conflicts.

    This function iterates through a sequence of dictionaries and merges them
    into a single new dictionary. If a key is present in more than one
    dictionary, it checks that the corresponding values are the exact same
    object using the `is` operator.

    Args:
        *dicts: A sequence of dictionaries to combine.

    Returns:
        A new dictionary containing the merged key-value pairs.

    Raises:
        ValueError: If a key exists in multiple dictionaries with values that
            are not the same object.
    """
    combined: dict[K, V] = {}
    for dict_ in dicts:
        for key, value in dict_.items():
            if key in combined:
                if combined[key] is not value:
                    msg = (
                        f"Key conflict for '{key}': "
                        f"existing value {combined[key]!r} is not the same as "
                        f"new value {value!r}."
                    )
                    raise ValueError(msg)
            else:
                combined[key] = value

    return combined


class Context(BaseModel):
    """Implementation of the :py:class:`~digout.core.context.ContextProtocol`."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    registries: Registries[Self] = Field(default_factory=lambda: Registries[Self]())
    """A mapping of registry names to :py:class:`~digout.registry.Registry` instances.
    """

    placeholders: dict[str, str] = Field(default_factory=dict[str, str])
    """A dictionary for passing dynamic values during a workflow run.

    Placeholders are used to supply runtime data to certain methods. For
    example, during the chunk phase, values like the chunk index or
    name can be passed
    to the :py:meth:`~digout.core.step.StepProtocol.has_run` and
    :py:meth:`~digout.core.step.StepProtocol.get_target` methods.
    """

    def combine(self, *others: Self) -> Self:
        """Combine this context with one or more other contexts.

        The ``registries`` and ``placeholders`` from all contexts are merged.
        The combination fails if a key exists in multiple contexts with a
        different value object.

        Args:
            *others: Other ``Context`` instances to combine with this one.

        Returns:
            A new ``Context`` instance with the combined data.
        """
        return self.__class__.model_validate(
            {
                "registries": _safely_combine_dictionaries(
                    self.registries, *(other.registries for other in others)
                ),
                "placeholders": _safely_combine_dictionaries(
                    self.placeholders, *(other.placeholders for other in others)
                ),
            }
        )

    def __repr__(self) -> str:
        """Return a developer-friendly string representation of the context."""
        return (
            self.__class__.__name__
            + f"(registries={self.registries!r}, placeholders={self.placeholders!r})"
        )

    def __str__(self) -> str:
        """Return a concise string representation of the placeholders."""
        return (
            self.__class__.__name__
            + "("
            + ", ".join(f"{key}={value!r}" for key, value in self.placeholders.items())
            + ")"
        )
