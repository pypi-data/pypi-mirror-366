"""Utility helpers for mapping compression codecs to canonical file extensions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Mapping

__all__ = ["get_extension_for", "merge_extensions"]

_COMPRESSION_TO_EXTENSION: Final[Mapping[str | None, str]] = {
    None: "",
    "gzip": "gz",
    "zstd": "zst",
    "brotli": "br",
}
"""Mapping of compression method to their canonical file extensions.

Only specify codecs whose canonical file extension deviates from the codec name.
"""


def get_extension_for(compression: str | None, /, *, with_dot: bool = True) -> str:
    """Return the canonical file-extension for *compression*.

    Args:
        compression: Compression codec name, e.g. ``gzip``.
            ``None`` means no compression.
        with_dot: If ``True``, the resulting extension is prefixed with ``.``.

    Returns:
        The extension string (without the leading dot unless *with_dot* is
        *True*).

    Examples:
        >>> extension_for("gzip", with_dot=True)
        '.gz'
        >>> extension_for("lz4", with_dot=False)
        'lz4'
        >>> extension_for(None)
        ''
    """
    extension = _COMPRESSION_TO_EXTENSION.get(compression, compression or "")
    return "." + extension if with_dot and extension else extension


def merge_extensions(*extensions: str | None) -> str:
    """Normalise and join *extensions* into a single dotted suffix.

    Args:
        *extensions: Individual extensions, with or without the leading ``.``.
            ``None`` or empty strings are silently ignored.

    Returns:
        A single string that starts with ``.``. If *extensions* is empty or
        all values are falsy, an empty string is returned.

    Example:
        >>> merge_extensions("csv", "gz")
        '.csv.gz'
    """
    parts: list[str] = [ext.lstrip(".") for ext in extensions if ext]
    return f".{'.'.join(parts)}" if parts else ""
