"""Debug utilities for the digout package."""

from __future__ import annotations


class DebugHalt(Exception):  # noqa: N818
    """Raised intentionally to stop execution for debugging purposes."""
