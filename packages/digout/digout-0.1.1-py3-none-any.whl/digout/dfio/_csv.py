"""A CSV DataFrame writer module using Pandas or PyArrow."""

from __future__ import annotations

from contextlib import nullcontext
from typing import TYPE_CHECKING, Annotated, Any, Literal

from pydantic import Discriminator

from ._base import DFIOBase
from ._extension import get_extension_for, merge_extensions

if TYPE_CHECKING:
    from pathlib import Path

    from pandas import DataFrame

__all__ = ["DFCSVIO", "DFCSVPandasIO", "DFCSVPyArrowIO"]


class DFCSVPandasIO(DFIOBase):
    """CSV I/O backed by **Pandas**."""

    type: Literal["csv"] = "csv"
    """Discriminator value that identifies the format. Always ``csv``."""

    engine: Literal["pandas"] = "pandas"
    """Discriminator value, always ``pandas``."""

    compression: Literal["infer", "gzip", "bz2", "zip", "xz", "zstd", "tar"] | None = (
        None
    )
    """Compression codec.

    Accepted by :py:meth:`pandas.DataFrame.to_csv` and :py:meth:`pandas.read_csv`.

    ``None`` means no compression, while ``infer`` allows Pandas to
    automatically detect the compression type based on the file extension.
    """

    def _write(self, df: DataFrame, path: Path, **kwargs: Any) -> None:
        kwargs.setdefault("index", False)
        df.to_csv(path, compression=self.compression, **kwargs)

    def _read(
        self, path: Path, columns: list[str] | None = None, **kwargs: Any
    ) -> DataFrame:
        """Read a DataFrame from a CSV file."""
        from pandas import read_csv  # noqa: PLC0415

        return read_csv(path, usecols=columns, compression=self.compression, **kwargs)

    def get_extension(self) -> str:
        return merge_extensions("csv", get_extension_for(self.compression))


class DFCSVPyArrowIO(DFIOBase):
    """CSV I/O backed by **PyArrow**."""

    type: Literal["csv"] = "csv"
    """Discriminator value that identifies the format. Always ``csv``."""

    engine: Literal["pyarrow"] = "pyarrow"
    """Engine to use for reading and writing CSV files, always 'pyarrow'."""

    compression: Literal["bz2", "brotli", "gzip", "lz4", "zstd"] | None = None
    """Compression method. None means no compression."""

    def _write(self, df: DataFrame, path: Path, **kwargs: Any) -> None:
        from pyarrow import CompressedOutputStream, Table  # noqa: PLC0415
        from pyarrow.csv import write_csv  # noqa: PLC0415

        table = Table.from_pandas(df)

        with (
            CompressedOutputStream(path, self.compression)
            if self.compression
            else nullcontext(path)
        ) as output_file:
            write_csv(table, output_file, **kwargs)

    def _read(
        self, path: Path, columns: list[str] | None = None, **kwargs: Any
    ) -> DataFrame:
        from pyarrow.csv import ReadOptions, read_csv  # noqa: PLC0415

        table = read_csv(path, read_options=ReadOptions(column_names=columns, **kwargs))
        return table.to_pandas()

    def get_extension(self) -> str:
        return merge_extensions("csv", get_extension_for(self.compression))


DFCSVIO = Annotated[DFCSVPandasIO | DFCSVPyArrowIO, Discriminator("engine")]
"""Run-time discriminated union of CSV DataFrame I/O classes.

Instantiate directly or let Pydantic pick the appropriate backend based on the
``engine`` field.
"""
