"""Defines the Pandera schema for the Velo hits-particles dataframe."""

from __future__ import annotations

import numpy as np
import pandera.pandas as pa

from ._base import (
    EVENT_ID_COLUMN,
    LHCB_ID_COLUMN,
    PARTICLE_ID_COLUMN,
    RUN_ID_COLUMN,
    add_metadata,
    compute_particle_id,
)

VELO_HITS_PARTICLES_SCHEMA = pa.DataFrameSchema(
    columns={
        "x": pa.Column(
            pa.Float32,
            title="hit x-coordinate",
            description=(
                "The vertical (x) position of the Velo hit "
                "in the plane transversal to the beam line, in mm."
            ),
            metadata={"func": lambda rf: np.concatenate(rf.arrays["Velo_x"])},
        ),
        "y": pa.Column(
            pa.Float32,
            title="hit y-coordinate",
            description=(
                "The horizontal (y) position of the Velo hit "
                "in the plane transversal to the beam line, in mm."
            ),
            metadata={"func": lambda rf: np.concatenate(rf.arrays["Velo_y"])},
        ),
        "z": pa.Column(
            pa.Float32,
            title="hit z-coordinate",
            description=(
                "The longitudinal (z) position of the Velo hit "
                "along the beam line, in mm."
            ),
            metadata={"func": lambda rf: np.concatenate(rf.arrays["Velo_z"])},
        ),
        "module": pa.Column(
            pa.Int32,
            checks=pa.Check.in_range(0, 51),
            title="Velo module number",
            description=(
                "The module number of the hit, from 0 to 51. The Velo has 52 modules."
            ),
            metadata={"func": lambda rf: np.concatenate(rf.arrays["Velo_Module"])},
        ),
        "sensor": pa.Column(
            pa.Int32,
            checks=pa.Check.in_range(0, 207),
            title="Velo sensor number",
            description=(
                "The sensor number of the hit, from 0 to 207. "
                "Each of the 52 modules has 4 sensors."
            ),
            metadata={"func": lambda rf: np.concatenate(rf.arrays["Velo_Sensor"])},
        ),
        "run_id": RUN_ID_COLUMN,
        "event_id": EVENT_ID_COLUMN,
        "lhcb_id": add_metadata(
            LHCB_ID_COLUMN,
            {"func": lambda rf: np.concatenate(rf.arrays["Velo_lhcbID"])},
        ),
        "particle_id": add_metadata(
            PARTICLE_ID_COLUMN,
            {"func": lambda rf: compute_particle_id(rf.arrays, "Velo_lhcbID")},
        ),
    },
    title="Velo hits-particles association",
    description=(
        "A dataframe of Velo hit information where each row represents "
        "the association between a single hit and a single particle."
    ),
    strict=True,
    coerce=True,
    unique=["run_id", "event_id", "lhcb_id", "particle_id"],
)
