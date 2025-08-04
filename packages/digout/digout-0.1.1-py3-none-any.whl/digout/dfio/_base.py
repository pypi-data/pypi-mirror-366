"""Core module for reading and writing DataFrames.

This module exposes :py:class:`DFWriterBase`, an abstract helper that provides a
thin façade around format-specific writer classes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

from .._utils.path import PathLike, create_directory

if TYPE_CHECKING:
    from collections.abc import Sequence

    from pandas import DataFrame

__all__ = ["DFIOBase"]

logger = getLogger(__name__)


class DFIOBase(BaseModel, ABC):
    """Base class for reading and writing DataFrames.

    It adds debug-level logging around DataFrame I/O.

    Subclasses must implement:

    * :py:meth:`_write`
    * :py:meth:`_read`
    * :py:meth:`get_extension`
    """

    # Abstract methods ===============================================================
    @abstractmethod
    def _write(self, df: DataFrame, path: Path, **kwargs: Any) -> None:
        """Write the DataFrame to the specified path.

        Args:
            df: The DataFrame to write.
            path: Destination path.
            **kwargs: Additional backend-specific keyword arguments.
        """
        ...

    @abstractmethod
    def _read(
        self, path: Path, columns: list[str] | None = None, **kwargs: Any
    ) -> DataFrame:
        """Read a DataFrame from the specified path.

        Args:
            path: Source path.
            columns: Optional list of columns to load. If ``None``, all columns
                are read.
            **kwargs: Additional backend-specific keyword arguments.

        Returns:
            DataFrame: The loaded DataFrame.
        """
        ...

    @abstractmethod
    def get_extension(self) -> str:
        """Return the canonical file extension.

        The string must include the leading dot and *may* contain
        further dots when multiple extensions are required (e.g. ``.csv.gz``).
        """

    # Public methods ================================================================
    def write(self, df: DataFrame, path: PathLike, **kwargs: Any) -> None:
        """Save the DataFrame to *path*.

        Args:
            df: The DataFrame to save.
            path: Destination path.
            **kwargs: Additional backend-specific keyword arguments.
        """
        path = Path(path)
        create_directory(path.parent)
        logger.debug("Writing DataFrame to '%s'", path)
        return self._write(df, Path(path), **kwargs)

    def read(
        self, path: PathLike, columns: Sequence[str] | None = None, **kwargs: Any
    ) -> DataFrame:
        """Read a DataFrame from *path*.

        Args:
            path: Source path.
            columns: Optional sequence of columns to load. If ``None``, all
                columns are read.
            **kwargs: Additional backend-specific keyword arguments.

        Returns:
            DataFrame: The loaded DataFrame.
        """
        path = Path(path)
        if columns is not None and not isinstance(columns, list):
            columns = list(columns)

        logger.debug("Reading DataFrame from '%s'", path)
        return self._read(path, columns=columns, **kwargs)

    def add_extension(self, path: PathLike) -> Path:
        """Add the appropriate file extension to the path.

        Args:
            path: The path to which the extension should be added.

        Returns:
            Path: The updated path with the appropriate file extension.
        """
        extension = self.get_extension()
        return Path(path).with_suffix(extension)
