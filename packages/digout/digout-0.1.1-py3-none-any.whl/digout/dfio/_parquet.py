"""Parquet DataFrame I/O backed by *PyArrow* or *Fastparquet*."""

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, Any, Literal

from ._base import DFIOBase
from ._extension import get_extension_for, merge_extensions

if TYPE_CHECKING:
    from pathlib import Path

    from pandas import DataFrame

logger = getLogger(__name__)

__all__ = ["DFParquetIO"]


class DFParquetIO(DFIOBase):
    """Parquet I/O backed by **PyArrow** or **Fastparquet**."""

    type: Literal["parquet"] = "parquet"
    """Discriminator value that identifies the format. Always ``parquet``."""

    compression: Literal["snappy", "gzip", "brotli", "lz4", "zstd"] | None = None
    """Compression codec. ``None`` means *no compression*."""

    engine: Literal["auto", "pyarrow", "fastparquet"] = "pyarrow"
    """Backend engine used by *pandas* :py:meth:`DataFrame.to_parquet`.

    ``pyarrow`` is the default and recommended engine for Parquet I/O.
    ``auto`` defers to Pandas to choose the first available backend.
    """

    def _write(self, df: DataFrame, path: Path, **kwargs: Any) -> None:
        kwargs.setdefault("index", False)
        df.to_parquet(path, compression=self.compression, engine=self.engine, **kwargs)

    def _read(
        self, path: Path, columns: list[str] | None = None, **kwargs: Any
    ) -> DataFrame:
        from pandas import read_parquet  # noqa: PLC0415

        return read_parquet(path, columns=columns, engine=self.engine, **kwargs)

    def get_extension(self) -> str:
        return merge_extensions("parquet", get_extension_for(self.compression))
