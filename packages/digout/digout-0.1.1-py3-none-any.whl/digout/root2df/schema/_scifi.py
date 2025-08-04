"""Defines the Pandera schema for the SciFi hits-particles dataframe."""

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

SCIFI_HITS_PARTICLES_SCHEMA = pa.DataFrameSchema(
    columns={
        "x": pa.Column(
            pa.Float32,
            title="Hit x-coordinate at Y=0",
            description="The vertical (x) position of the SciFi hit at y=0, in mm.",
            metadata={"func": lambda rf: np.concatenate(rf.arrays["FT_x"])},
        ),
        "z": pa.Column(
            pa.Float32,
            title="Hit z-coordinate",
            description=(
                "The longitudinal position (z) of the SciFi hit along the beam line, "
                "in mm."
            ),
            metadata={"func": lambda rf: np.concatenate(rf.arrays["FT_z"])},
        ),
        "w": pa.Column(
            pa.Float32,
            title="Hit weight error",
            description=(
                "The hit weight error from the SciFi clustering algorithm, in mm."
            ),
            metadata={"func": lambda rf: np.concatenate(rf.arrays["FT_w"])},
        ),
        "dxdy": pa.Column(
            pa.Float32,
            title="Fibre dx/dy slope",
            description=(
                "The slope (dx/dy) of the SciFi fibre. "
                "This is the tangent of the fibre's stereo angle, "
                "with possible values corresponding to 0, +5, and -5 degrees "
                "for x, u, and v planes, respectively."
            ),
            metadata={"func": lambda rf: np.concatenate(rf.arrays["FT_dxdy"])},
        ),
        "ymin": pa.Column(
            pa.Float32,
            title="Hit y-min",
            description=(
                "The minimum y-coordinate of the SciFi hit, "
                "corresponding to the bottom of the fibre, in mm."
            ),
            metadata={"func": lambda rf: np.concatenate(rf.arrays["FT_YMin"])},
        ),
        "ymax": pa.Column(
            pa.Float32,
            title="Hit y-max",
            description=(
                "The maximum y-coordinate of the SciFi hit, "
                "corresponding to the top of the fibre, in mm."
            ),
            metadata={"func": lambda rf: np.concatenate(rf.arrays["FT_YMax"])},
        ),
        "hit_plane_code": pa.Column(
            pa.Int32,
            checks=pa.Check.in_range(0, 11),
            title="Hit plane code",
            description=(
                "The plane or layer number of the hit, from 0 to 11. "
                "The SciFi detector has 3 stations, each with 4 planes."
            ),
            metadata={"func": lambda rf: np.concatenate(rf.arrays["FT_hitPlaneCode"])},
        ),
        "hit_zone": pa.Column(
            pa.Int32,
            checks=pa.Check.in_range(0, 23),
            title="Hit zone",
            description=(
                "The zone number of the hit, from 0 to 23. "
                "Each SciFi plane is divided into a left and right zone."
            ),
            metadata={"func": lambda rf: np.concatenate(rf.arrays["FT_hitzone"])},
        ),
        "run_id": RUN_ID_COLUMN,
        "event_id": EVENT_ID_COLUMN,
        "particle_id": add_metadata(
            PARTICLE_ID_COLUMN,
            {"func": lambda rf: compute_particle_id(rf.arrays, "FT_lhcbID")},
        ),
        "lhcb_id": add_metadata(
            LHCB_ID_COLUMN,
            {"func": lambda rf: np.concatenate(rf.arrays["FT_lhcbID"])},
        ),
    },
    title="SciFi hits-particles association",
    description=(
        "A dataframe of SciFi hit information where each row represents "
        "the association between a single hit and a single particle."
    ),
    strict=True,
    coerce=True,
    unique=["run_id", "event_id", "lhcb_id", "particle_id"],
)
