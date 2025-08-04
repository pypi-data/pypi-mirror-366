"""Formatting utilities for strings with partial arguments."""

from __future__ import annotations

from string import Formatter
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

__all__ = ["partial_format"]


class _PartialFormatter(Formatter):
    """Class used for formatting not all the arguments of a string.

    Taken from
    https://stackoverflow.com/questions/17215400/format-string-unused-named-arguments
    """

    def __init__(self, default: str = "{{{0}}}") -> None:
        """Initialize the formatter with a default value for missing keys."""
        self.default = default

    def get_value(
        self, key: int | str, args: Sequence[Any], kwargs: Mapping[str, Any]
    ) -> Any:
        if isinstance(key, str):
            return kwargs.get(key, self.default.format(key))
        else:
            return super().get_value(key, args, kwargs)


_fmt = _PartialFormatter()


def partial_format(string: str, *args: Any, **kwargs: Any) -> str:
    """Format a string with only the provided arguments.

    The arguments that are not provided are left as they are.

    Args:
        string: String to format.
        *args: Positional arguments to format the string.
        **kwargs: Arguments to format the string.

    Returns:
        Formatted string.

    Examples:
        >>> partial_format("{a}{b}", a="blabla")
        'blabla{b}'
    """
    return _fmt.format(string, *args, **kwargs)
