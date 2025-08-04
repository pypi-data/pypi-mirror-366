"""Define the Pandera schema for the ``event`` dataframe."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

import numpy as np
import pandera.pandas as pa

from ._base import EVENT_ID_COLUMN, RUN_ID_COLUMN

if TYPE_CHECKING:
    from numpy.typing import NDArray

T = TypeVar("T", bound=np.generic)


def _get_unique(array: NDArray[T]) -> T:
    """Return the single unique value from an array.

    This function is used to extract a scalar value that is expected to be
    constant across all entries for a given event.

    Args:
        array: The input array.

    Returns:
        The single unique value present in the array.

    Raises:
        ValueError: If the array is empty or contains more than one unique value.
    """
    unique_values = np.unique(array)
    if unique_values.size == 0:
        msg = "Array is empty, cannot get unique values"
        raise ValueError(msg)
    if unique_values.size > 1:
        msg = "Array has more than one unique value"
        raise ValueError(msg)
    return unique_values[0]


EVENTS_SCHEMA = pa.DataFrameSchema(
    columns={
        "n_velo_hits": pa.Column(
            pa.Int32,
            checks=pa.Check.ge(0),
            title="Number of Velo hits",
            description="The total number of hits in the Velo detector for the event.",
            metadata={"func": lambda rf: [_get_unique(rf.arrays["nbHits_in_Velo"])]},
        ),
        "n_scifi_hits": pa.Column(
            pa.Int32,
            checks=pa.Check.ge(0),
            title="Number of SciFi hits",
            description="The total number of hits in the SciFi detector for the event.",
            metadata={"func": lambda rf: [_get_unique(rf.arrays["nbHits_in_SciFi"])]},
        ),
        "n_ut_hits": pa.Column(
            pa.Int32,
            checks=pa.Check.ge(0),
            title="Number of UT hits",
            description="The total number of hits in the UT detector for the event.",
            metadata={"func": lambda rf: [_get_unique(rf.arrays["nbHits_in_UT"])]},
        ),
        "run_id": RUN_ID_COLUMN,
        "event_id": EVENT_ID_COLUMN,
    },
    coerce=True,
    strict=True,
    title="Event",
    description=(
        "A dataframe of event information, where each row represents a a single event."
    ),
    unique=["run_id", "event_id"],
)
