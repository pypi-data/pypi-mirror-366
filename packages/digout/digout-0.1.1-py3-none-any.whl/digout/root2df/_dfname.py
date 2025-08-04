"""Defines the recognized names for dataframes produced by the ``ROOT2DFStep``.

This module provides a ``Literal`` type alias and a corresponding set of constants
for the dataframe names. Using these ensures consistency and enables static type
checking.
"""

from __future__ import annotations

from typing import Final, Literal

DFName = Literal[
    "particles",
    "velo_hits_particles",
    "scifi_hits_particles",
    "ut_hits_particles",
    "events",
]
"""A ``Literal`` type alias for the valid dataframe names."""

DFNAMES: Final[set[DFName]] = {
    "particles",
    "velo_hits_particles",
    "scifi_hits_particles",
    "ut_hits_particles",
    "events",
}
"""A set containing all valid dataframe names for runtime validation."""
