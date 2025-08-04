"""Provides a function for writing dataframes to disk using a ``DFIO`` backend."""

from __future__ import annotations

from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .._utils.path import create_directory

if TYPE_CHECKING:
    from collections.abc import Mapping

    from pandas import DataFrame

    from ..dfio import DFIOBase


logger = getLogger(__name__)


def write_dataframes(
    dataframes: Mapping[Any, DataFrame],
    output_paths: Mapping[Any, str | Path],
    io: DFIOBase,
) -> None:
    """Write a collection of Pandas DataFrames to their respective file paths.

    This function iterates through the provided dataframes, ensures the output
    directory exists for each, and then uses the specified
    :py:class:`~digout.dfio.DFIOBase` object to handle the serialization
    and writing to disk (e.g., as a CSV or Parquet file).

    Args:
        dataframes: A dictionary mapping identifiers (e.g., dataframe names) to
            their corresponding ``pd.DataFrame`` objects.
        output_paths: A dictionary mapping the same identifiers to the file
            paths where the dataframes should be saved.
        io: The :py:class:`~digout.dfio.DFIOBase` instance that implements
            the specific file writing logic.

    Raises:
        ValueError: If an output path is not provided for a dataframe that is
            present in the ``dataframes`` dictionary.
    """
    for dfname, dataframe in dataframes.items():
        output_path = output_paths.get(dfname)
        if output_path is None:
            msg = f"No output path provided for DataFrame '{dfname}'."
            raise ValueError(msg)
        output_path = Path(output_path)
        create_directory(output_path.parent)

        logger.info("Saving DataFrame '%s' to '%s'", dfname, output_path)
        io.write(dataframe, output_path)
