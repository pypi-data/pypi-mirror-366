"""Provide a function for validating a collection of dataframes using Pandera."""

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Mapping

    from pandas import DataFrame
    from pandera.pandas import DataFrameSchema


logger = getLogger(__name__)


def validate_dataframes(
    dataframes: Mapping[Any, DataFrame], schemas: Mapping[Any, DataFrameSchema]
) -> None:
    """Validate a dictionary of dataframes against a corresponding dictionary of schemas.

    This function iterates through the ``dataframes`` and validates each one
    against the Pandera schema with the same key in the ``schemas`` dictionary.
    The validation is performed in-place, which means data types may be coerced
    as defined in the schema.

    Args:
        dataframes: A dictionary mapping identifiers (e.g., dataframe names) to
            the ``pd.DataFrame`` objects to be validated.
        schemas: A dictionary mapping the same identifiers to their corresponding
            ``pandera.DataFrameSchema`` objects.

    Raises:
        pandera.errors.SchemaError: If any dataframe fails validation against
            its schema.
        KeyError: If a dataframe name exists in ``dataframes`` but not in ``schemas``.
    """  # noqa: E501
    for dfname, dataframe in dataframes.items():
        schema = schemas[dfname]
        schema.validate(dataframe, inplace=True)
        logger.debug("Validated dataframe '%s' against its schema", dfname)
