"""Provide Pandera schemas for the dataframes created by the ROOT2DF step.

This package defines a ``pandera.DataFrameSchema`` for each type of dataframe
produced by the :py:class:`~digout.step.root2df.ROOT2DFStep` step
(e.g., events, particles, Velo hits).

The main entry points are the :py:func:`get_schema` and :py:func:`get_schemas`
functions, which provide a convenient way to retrieve these schemas,
optionally selecting a subset of columns.
"""

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING

from .._dfname import DFNAMES, DFName
from ._event import EVENTS_SCHEMA
from ._particle import PARTICLES_SCHEMA
from ._scifi import SCIFI_HITS_PARTICLES_SCHEMA
from ._ut import UT_HITS_PARTICLES_SCHEMA
from ._velo import VELO_HITS_PARTICLES_SCHEMA

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    import pandera.pandas as pa

logger = getLogger(__name__)

__all__ = ["SCHEMAS", "get_schema", "get_schemas"]


SCHEMAS: dict[DFName, pa.DataFrameSchema] = {
    "velo_hits_particles": VELO_HITS_PARTICLES_SCHEMA,
    "scifi_hits_particles": SCIFI_HITS_PARTICLES_SCHEMA,
    "ut_hits_particles": UT_HITS_PARTICLES_SCHEMA,
    "particles": PARTICLES_SCHEMA,
    "events": EVENTS_SCHEMA,
}
"""A mapping from dataframe names to their corresponding Pandera schemas."""

assert set(SCHEMAS.keys()) == DFNAMES, (
    "The keys of _SCHEMAS must match the DFNAMES set. "
    f"Current keys: {set(SCHEMAS.keys())}, DFNAMES: {set(DFNAMES)}"
)


def get_schema(
    dfname: DFName, columns: Sequence[str] | None = None
) -> pa.DataFrameSchema:
    """Retrieve the Pandera schema for a single dataframe.

    Args:
        dfname: The name of the dataframe for which to get the schema.
        columns: An optional list of column names to select from the full
            schema. If ``None``, the complete schema is returned.

    Returns:
        The requested ``pandera.DataFrameSchema``.

    Raises:
        ValueError: If ``dfname`` is not a recognized dataframe name.
    """
    logger.debug("Getting schema for DataFrame '%s'", dfname)
    schema = SCHEMAS.get(dfname)
    if schema is None:
        msg = f"Schema for '{dfname}' not found. Available schemas are: " + ", ".join(
            SCHEMAS.keys()
        )
        raise ValueError(msg)

    if columns is not None:
        # Select only the specified columns from the schema
        schema = schema.select_columns(list(columns))

    return schema


def get_schemas(
    dfname_to_columns: Mapping[DFName, Sequence[str] | None] | None = None,
) -> dict[DFName, pa.DataFrameSchema]:
    """Retrieve a dictionary of Pandera schemas for multiple dataframes.

    Args:
        dfname_to_columns: An optional dictionary mapping each dataframe name to
            a list of columns to select. If a dataframe name is not in the
            dictionary, it will not be included in the output. If the value
            for a key is ``None``, all columns for that schema are selected.
            If the entire argument is ``None``, all schemas are returned in full.

    Returns:
        A dictionary mapping dataframe names to their ``pandera.DataFrameSchema``.
    """
    if dfname_to_columns is None:
        return SCHEMAS
    return {
        dfname: get_schema(dfname, columns)
        for dfname, columns in dfname_to_columns.items()
    }
