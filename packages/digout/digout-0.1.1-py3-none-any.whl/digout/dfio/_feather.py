"""Feather DataFrame I/O backed by PyArrow."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final, Literal

from ._base import DFIOBase
from ._extension import get_extension_for, merge_extensions

if TYPE_CHECKING:
    from pathlib import Path

    from pandas import DataFrame

__all__ = ["DFFeatherIO"]

_UNCOMPRESSED_SENTINEL: Final[str] = "uncompressed"
"""Sentinel value used by PyArrow to denote no compression."""


def _get_arrow_compression(
    compression: Literal["zstd", "lz4"] | None,
) -> Literal["zstd", "lz4", "uncompressed"]:
    return compression if compression is not None else _UNCOMPRESSED_SENTINEL  # type: ignore[return-value]


class DFFeatherIO(DFIOBase):
    """Feather I/O backed by **PyArrow**.

    Notes:
        PyArrow expects the literal string ``uncompressed`` when no compression is
        used. To keep the public API symmetrical with other *dfio* back-ends, the
        ``compression`` field therefore accepts ``None`` to denote “no compression”,
        and translates this sentinel internally.
    """

    type: Literal["feather"] = "feather"
    """Discriminator value that identifies the format. Always ``feather``."""

    compression: Literal["zstd", "lz4"] | None = None
    """Compression codec.

    ``None`` means no compression (encoded as``uncompressed`` in PyArrow).
    """

    compression_level: int | None = None
    """Codec-specific compression level. ``None`` means Arrow default."""

    chunksize: int | None = None
    """Number of rows per chunk when writing. ``None`` lets Arrow choose."""

    def _write(self, df: DataFrame, path: Path, **kwargs: Any) -> None:
        from pyarrow.feather import write_feather  # noqa: PLC0415

        write_feather(
            df,
            path,
            compression=_get_arrow_compression(self.compression),
            compression_level=self.compression_level,
            chunksize=self.chunksize,
            **kwargs,
        )

    def _read(
        self, path: Path, columns: list[str] | None = None, **kwargs: Any
    ) -> DataFrame:
        from pyarrow.feather import read_feather  # noqa: PLC0415

        return read_feather(path, columns=columns, **kwargs)

    def get_extension(self) -> str:
        return merge_extensions("feather", get_extension_for(self.compression))
