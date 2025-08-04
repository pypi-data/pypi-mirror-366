"""Defines reusable base columns and helper functions for Pandera schemas.

This module contains common ``pandera.Column`` definitions (e.g., for event IDs,
particle IDs) and utility functions that are shared across the different
dataframe schemas.
"""

from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, Any, TypeVar

import numpy as np
import pandera.pandas as pa
from pandera.api.pandas.array import ArraySchema

if TYPE_CHECKING:
    from collections.abc import Mapping

    from numpy.typing import NDArray

LHCB_ID_COLUMN = pa.Column(
    pa.UInt32,
    title="LHCb ID",
    description=(
        "A unique identifier for a detector channel. "
        "This is used to identify a recorded hit or cluster."
    ),
)
RUN_ID_COLUMN = pa.Column(
    pa.UInt32,
    title="Run ID",
    description="The unique identifier for a data-taking run.",
    metadata={"func": lambda rf: rf.run_id},
)
EVENT_ID_COLUMN = pa.Column(
    pa.UInt32,
    title="Event ID",
    description="The unique identifier for an event within a run.",
    metadata={"func": lambda rf: rf.event_id},
)
PARTICLE_ID_COLUMN = pa.Column(
    pa.Int32,
    checks=pa.Check.ge(0),
    title="Particle ID",
    description=(
        "The unique identifier for a particle that created a hit. "
        "A value of 0 indicates a noise hit not associated with any particle."
    ),
)


A = TypeVar("A", bound=ArraySchema)


def add_metadata(array_schema: A, metadata: dict[str, Any]) -> A:
    """Create a copy of a Pandera ``ArraySchema`` with added metadata.

    This helper function is used to attach a data-creation function (``func``)
    to a base column definition without modifying the original.

    Args:
        array_schema: The Pandera array schema to which metadata will be added.
        metadata: A dictionary of metadata to add to the schema's existing
            metadata.

    Returns:
        A new Pandera array schema instance with the updated metadata.
    """
    new_schema = deepcopy(array_schema)
    if new_schema.metadata is None:
        new_schema.metadata = {}
    new_schema.metadata.update(metadata)
    return new_schema


def compute_particle_id(
    arrays: Mapping[str, NDArray[Any]], name: str
) -> NDArray[np.int32]:
    """Compute the per-hit particle ID for a detector subsystem.

    This function maps the particle keys from the raw ROOT file to the flattened
    array of hits, assigning a particle ID to each individual hit.

    The logic is as follows:
    1. The ``key`` array from the ROOT file contains particle indices. It is
       shifted by +1 to start real particle IDs from 1.
    2. The last element of the ``key`` array, which is a sentinel for noise, is
       mapped to a particle ID of 0.
    3. This new array of particle IDs is then repeated for each hit produced by
       the corresponding particle.

    Args:
        arrays: A mapping of arrays from the ROOT file, which must include
            ``key`` (the particle keys) and the hit array specified by ``name``.
        name: The name of the jagged hit array (e.g., ``Velo_lhcbID``).

    Returns:
        A 1D array of particle IDs, with one entry per hit.
    """
    if not (mask := ((arrays["key"] > 0) | (arrays["key"] == -999999))).all():
        msg = (
            "The 'key' array is expected to contain only positive values or -999999. "
            "Found non-positive values in the 'key' array: "
            + ", ".join(map(str, arrays["key"][~mask]))
            + "."
        )
        raise ValueError(msg)

    return np.repeat(
        # Last element replaced by 0 instead of -999999
        np.concatenate([arrays["key"][:-1] + 1, [0]]),
        [x.size for x in arrays[name]],
    )
