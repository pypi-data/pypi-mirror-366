"""Provide the logic and public API for the ROOT to DataFrame conversion.

This package orchestrates the conversion of ``PrTrackerDumper`` ROOT files into
structured and validated Pandas DataFrames. It combines functionality from its
submodules for schema definition, data conversion, validation, and writing.

The main entry point is the high-level :py:func:`root2df` function, which performs the
entire end-to-end process.
"""

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING

from ._conversion import (
    compute_and_concatenate_dataframes as _compute_and_concatenate_dataframes,
)
from ._dfname import DFNAMES, DFName
from ._validation import validate_dataframes
from ._writing import write_dataframes
from .schema import SCHEMAS, get_schema, get_schemas

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from pathlib import Path

    from pandas import DataFrame
    from pandera.pandas import DataFrameSchema

    from ..dfio import DFIO


logger = getLogger(__name__)


__all__ = [  # noqa: RUF022
    "DFNAMES",
    "DFName",
    "SCHEMAS",
    "get_schema",
    "get_schemas",
    "root2df",
    "validate_dataframes",
]


def root2df(
    input_dir: Path,
    dfio: DFIO,
    dfname_to_output_path: Mapping[DFName, str | Path],
    dfname_to_columns: Mapping[DFName, Sequence[str] | None] | None = None,
) -> tuple[dict[DFName, DataFrame], dict[DFName, DataFrameSchema]]:
    """Perform the end-to-end conversion of ROOT files to validated DataFrames.

    This function orchestrates the full conversion pipeline:

    1.  Retrieves the appropriate Pandera schemas for the requested dataframes.
    2.  Finds all ``.root`` files in the input directory.
    3.  Reads the ROOT files, computes the columns, and concatenates the data.
    4.  Validates the resulting dataframes against their schemas, coercing types.
    5.  Writes the final, validated dataframes to disk.

    Args:
        input_dir: The directory containing the input ``.root`` files.
        dfio: The ``DFIO`` instance used for writing the output files.
        dfname_to_output_path: A mapping from each dataframe name to its
            destination file path.
        dfname_to_columns: An optional mapping to specify which dataframes to
            create and which columns to include. If ``None``, all dataframes and
            all columns are processed.

    Returns:
        A tuple containing two dictionaries:

        1. A mapping from dataframe names to the in-memory,
           validated ``pd.DataFrame`` objects.
        2. A mapping from dataframe names to the ``pandera.DataFrameSchema`` objects
           used.

    Raises:
        RuntimeError: If no ``.root`` files are found in ``input_dir``.
    """
    if dfname_to_columns:
        # Filter out empty column lists to avoid creating empty dataframes.
        dfname_to_columns = {
            dfname: columns or None
            for dfname, columns in dfname_to_columns.items()
            if columns is None or columns
        }
    schemas = get_schemas(dfname_to_columns=dfname_to_columns)

    input_paths = sorted(input_dir.glob("*.root"))

    if not input_paths:
        msg = f"No ROOT files found in the input directory: '{input_dir}'."
        raise RuntimeError(msg)

    logger.debug(
        "Found %d ROOT files in the input directory: '%s'.", len(input_paths), input_dir
    )

    dataframes = _compute_and_concatenate_dataframes(paths=input_paths, schemas=schemas)
    validate_dataframes(dataframes, schemas)
    write_dataframes(dataframes=dataframes, output_paths=dfname_to_output_path, io=dfio)
    return dataframes, schemas
