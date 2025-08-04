"""Provide functions for converting ``PrTrackerDumper`` ROOT files into DataFrames.

This module contains the core logic for reading the specific TTree structure produced
by the ``PrTrackerDumper`` algorithm, extracting data using ``uproot``, and
transforming it into structured Pandas DataFrames according to Pandera schemas.
"""

from __future__ import annotations

import re
from functools import cached_property
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeVar

import numpy as np
import pandas as pd
import uproot  # type: ignore[import-untyped]
from pandera.api.pandas.array import ArraySchema

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    from numpy.typing import NDArray
    from pandera.pandas import DataFrameSchema


logger = getLogger(__name__)

K = TypeVar("K")

__all__ = ["compute_and_concatenate_dataframes", "compute_dataframes"]


class _PrTrackerDumperFile:
    """A wrapper for a single ROOT file produced by ``PrTrackerDumper``.

    This class provides a convenient interface for accessing the TTree data and
    extracting metadata (run and event ID) from the file name. Data is loaded
    lazily and cached.
    """

    def __init__(self, path: str | Path) -> None:
        """Initialize the wrapper with the path to the ROOT file."""
        self.path = path
        """Path to a PrTrackerDumper ROOT file."""

    @cached_property
    def _run_id_event_id(self) -> tuple[np.uint32, np.uint32]:
        """Parses the run and event numbers from the ROOT file name."""
        filename = Path(self.path).name
        m = re.match(r"^DumperFTUTHits_runNb_(\d+)_evtNb_(\d+)\.root$", filename)
        if m is None:
            msg = f"File name '{filename}' does not match expected format"
            raise ValueError(msg)
        return np.uint32(m.group(1)), np.uint32(m.group(2))

    @cached_property
    def arrays(self) -> dict[str, NDArray[Any]]:
        """Lazily loads and returns the TTree data as a dictionary of NumPy arrays."""
        rfile = uproot.open(self.path)
        logger.debug("Opened ROOT file: %s", self.path)
        up_hits_detectors = rfile["Hits_detectors"]
        if not isinstance(up_hits_detectors, uproot.TTree):
            msg = f"Expected a TTree, got {type(up_hits_detectors)}"
            raise TypeError(msg)
        return up_hits_detectors.arrays(library="np")

    @property
    def run_id(self) -> np.uint32:
        """The run ID extracted from the file name."""
        return self._run_id_event_id[0]

    @property
    def event_id(self) -> np.uint32:
        """The event ID extracted from the file name."""
        return self._run_id_event_id[1]


def __compute_column(
    dfname: object,
    column_name: str,
    column_schema: ArraySchema[Any] | None,
    dumper_file: _PrTrackerDumperFile,
) -> object:
    """Compute the data for a single DataFrame column using a function from its schema.

    This function extracts the data creation function (``func``) from the
    ``metadata`` of a column's Pandera schema and executes it.

    Args:
        dfname: The name of the dataframe (used for logging).
        column_name: The name of the column to compute.
        column_schema: The ``pandera.ArraySchema`` for the column.
        dumper_file: The :py:class:`_PrTrackerDumperFile` instance providing
            the raw data.

    Returns:
        The computed column data (typically a NumPy array but could be a constant
        value to broadcast).

    Raises:
        AssertionError: If the schema's metadata is malformed.
    """
    assert isinstance(column_schema, ArraySchema), (
        f"Column '{column_name}' in schema '{dfname}' is not a Pandera ArraySchema "
        f"but {type(column_schema)}."
    )

    metadata = column_schema.metadata
    assert metadata is not None, (
        f"Column '{column_name}' in schema '{dfname}' has no metadata."
    )

    func = metadata.get("func")
    assert func is not None, (
        f"Column '{column_name}' in schema '{dfname}' has no 'func' metadata."
    )
    assert callable(func), (
        f"Column '{column_name}' in schema '{dfname}' has 'func' metadata "
        f"that is not callable: {func}"
    )

    logger.debug("Computing array for column '%s' in schema '%s'", column_name, dfname)
    return func(dumper_file)


def _compute_dataframe(
    dumper_file: _PrTrackerDumperFile, dfname: object, schema: DataFrameSchema
) -> pd.DataFrame:
    """Construct a single Pandas DataFrame from a ROOT file based on a schema.

    This function iterates over the columns defined in the ``schema`` and uses the
    ``func`` metadata of each column to generate the corresponding data series.

    Args:
        dumper_file: The wrapper for the source ROOT file.
        dfname: The name of the dataframe being created (for logging).
        schema: The ``pandera.DataFrameSchema`` that defines the structure and
            data creation logic for the dataframe.

    Returns:
        A new Pandas DataFrame.
    """
    columns = {}
    for column_name, pa_column in schema.columns.items():
        if not isinstance(pa_column, ArraySchema):
            msg = (
                f"Column '{column_name}' in schema '{dfname}' "
                f"is not a Pandera ArraySchema but {type(pa_column)}."
            )
            raise TypeError(msg)

        columns[column_name] = __compute_column(
            dfname, column_name, pa_column, dumper_file
        )
    return pd.DataFrame(columns)


def compute_dataframes(
    path: str | Path, schemas: Mapping[K, DataFrameSchema]
) -> dict[K, pd.DataFrame]:
    """Create a set of DataFrames from a single ``PrTrackerDumper`` ROOT file.

    Args:
        path: The path to the input ROOT file.
        schemas: A dictionary mapping dataframe names to their corresponding
            ``pandera.DataFrameSchema`` objects.

    Returns:
        A dictionary mapping each dataframe name to its computed ``pd.DataFrame``.
    """
    # Create a PrTrackerDumperFile instance
    dumper_file = _PrTrackerDumperFile(path)

    # Form dataframes for each file
    dataframes = {
        dfname: _compute_dataframe(dumper_file, dfname, schema)
        for dfname, schema in schemas.items()
    }
    logger.debug("Computed dataframes for path '%s'", path)
    return dataframes


def compute_and_concatenate_dataframes(
    paths: Iterable[str | Path], schemas: Mapping[K, DataFrameSchema]
) -> dict[K, pd.DataFrame]:
    """Create and concatenate DataFrames from multiple ROOT files.

    This function processes each ROOT file in ``paths``, generates a set of
    dataframes for each file according to the ``schemas``, and then concatenates
    the dataframes for each type into a single, combined dataframe.

    Args:
        paths: An iterable of paths to the input ROOT files.
        schemas: A dictionary mapping dataframe names to their Pandera schemas.

    Returns:
        A dictionary mapping each dataframe name to a single, concatenated
        ``pd.DataFrame``.
    """
    file_to_dataframes: dict[K, list[pd.DataFrame]] = {
        file_name: [] for file_name in schemas
    }

    for path in paths:
        dataframes = compute_dataframes(path, schemas)
        for dfname, df in dataframes.items():
            file_to_dataframes[dfname].append(df)

    return {
        dfname: pd.concat(dfs, ignore_index=True)
        for dfname, dfs in file_to_dataframes.items()
    }
