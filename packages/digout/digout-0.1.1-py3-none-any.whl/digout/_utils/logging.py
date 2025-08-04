"""Logging utility for the digout package."""

from __future__ import annotations

import logging
from typing import Any, Literal, TypeAlias

logger = logging.getLogger(__name__)

__all__ = ["DEFAULT_LOG_LEVEL", "LOG_LEVELS", "LogLevel", "setup_basic_logging"]


def setup_basic_logging(level: int | LogLevel, **kwargs: Any) -> None:
    """Set up basic logging configuration.

    Args:
        level: The logging level to set. Can be an integer (e.g., logging.DEBUG)
            or a string (e.g., "DEBUG", "INFO", etc.).
        **kwargs: Additional keyword arguments to pass to `logging.basicConfig`.

    Raises:
        ValueError: If the provided log level is not valid.
        TypeError: If the log level is not an integer or a valid string.
    """
    if isinstance(level, str):
        if level not in LOG_LEVELS:
            msg = (
                f"Invalid log level string: {level}. "
                "Must be one of " + ", ".join(map(repr, LOG_LEVELS)) + "."
            )
            raise ValueError(msg)
        try:
            level = getattr(logging, level.upper())
        except AttributeError:
            msg = f"Invalid log level: {level}"
            raise ValueError(msg) from None

        assert isinstance(level, int), "Log level must be an integer."

    root = logging.getLogger()
    if root.handlers:
        root.handlers.clear()

    kwargs.setdefault("format", "%(asctime)s [%(levelname)-8s] %(message)s")
    kwargs.setdefault("datefmt", "%Y-%m-%d %H:%M:%S")

    logging.basicConfig(level=level, **kwargs)

    logger.debug(
        "Basic logging setup complete with level: %s", logging.getLevelName(level)
    )


LogLevel: TypeAlias = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
"""Type alias for log levels."""

LOG_LEVELS: list[LogLevel] = [
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
]
"""List of valid log levels."""

DEFAULT_LOG_LEVEL: LogLevel = "INFO"
"""Default log level."""
