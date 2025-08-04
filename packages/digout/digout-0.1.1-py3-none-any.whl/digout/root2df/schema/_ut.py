"""Defines the Pandera schema for the UT hits-particles dataframe."""

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

UT_HITS_PARTICLES_SCHEMA = pa.DataFrameSchema(
    columns={
        "dxdy": pa.Column(
            pa.Float32,
            title="Strip dx/dy slope",
            description=(
                "The slope (dx/dy) of the UT strip. "
                "This is the tangent of the strip's stereo angle, "
                "with possible values corresponding to 0, +5, and -5 degrees "
                "for x, u, and v planes, respectively."
            ),
            metadata={"func": lambda rf: np.concatenate(rf.arrays["UT_dxDy"])},
        ),
        "cos": pa.Column(
            pa.Float32,
            title="Cosine of the strip stereo angle",
            description=(
                "The cosine of the UT strip's stereo angle relative to the x-axis."
            ),
            metadata={"func": lambda rf: np.concatenate(rf.arrays["UT_cos"])},
        ),
        "tan_t": pa.Column(
            pa.Float32,
            title="Tangent of the negative strip angle with respect to the x-axis",
            description=(
                "The tangent of the strip's angle with the sign flipped, "
                "computed as `-dxdy`."
            ),
            metadata={"func": lambda rf: np.concatenate(rf.arrays["UT_tanT"])},
        ),
        "cos_t": pa.Column(
            pa.Float32,
            title="Cosine of negative strip angle",
            description=(
                "Cosine of the negative strip angle with respect to the x-axis, "
                "recomputed as `1 / sqrt(1 + tan_t**2)` if the hit's x-coordinate "
                "at y=0 is very close to 0."
            ),
            metadata={"func": lambda rf: np.concatenate(rf.arrays["UT_cosT"])},
        ),
        "sin_t": pa.Column(
            pa.Float32,
            title="Sine of negative strip angle",
            description=(
                "The sine of the negative stereo angle, computed as `tan_t * cos_t`."
            ),
            metadata={"func": lambda rf: np.concatenate(rf.arrays["UT_sinT"])},
        ),
        "plane_code": pa.Column(
            pa.Int32,
            checks=pa.Check.in_range(0, 3),
            title="UT plane code",
            description=(
                "The plane number of the hit, from 0 to 3. "
                "The UT detector has 4 planes."
            ),
            metadata={"func": lambda rf: np.concatenate(rf.arrays["UT_planeCode"])},
        ),
        "size": pa.Column(
            pa.Int32,
            checks=pa.Check.ge(1),
            title="Cluster size",
            description="The number of strips in the UT cluster.",
            metadata={"func": lambda rf: np.concatenate(rf.arrays["UT_size"])},
        ),
        "weight": pa.Column(
            pa.Float32,
            title="Cluster weight",
            description=(
                "The weight from the UT clustering algorithm. "
                "Larger values indicate a more reliable hit."
            ),
            metadata={"func": lambda rf: np.concatenate(rf.arrays["UT_weight"])},
        ),
        "xt": pa.Column(
            pa.Float32,
            title="XT",
            description="The same as the ``cos`` column.",
            metadata={"func": lambda rf: np.concatenate(rf.arrays["UT_xT"])},
        ),
        "xatyeq0": pa.Column(
            pa.Float32,
            title="x-coordinate at y=0",
            description="The x-coordinate of the UT hit at y=0, in mm.",
            metadata={"func": lambda rf: np.concatenate(rf.arrays["UT_xAtYEq0"])},
        ),
        "xatymid": pa.Column(
            pa.Float32,
            title="x-coordinate at y-mid",
            description=(
                "The x-coordinate of the UT hit at the middle of the strip, in mm."
            ),
            metadata={"func": lambda rf: np.concatenate(rf.arrays["UT_xAtYMid"])},
        ),
        "ybegin": pa.Column(
            pa.Float32,
            title="Strip y-begin",
            description=(
                "The y-coordinate of one end of the physical UT strip, in mm."
            ),
            metadata={"func": lambda rf: np.concatenate(rf.arrays["UT_yBegin"])},
        ),
        "yend": pa.Column(
            pa.Float32,
            title="Strip y-end",
            description=(
                "The y-coordinate of the other end of the physical UT strip, in mm."
            ),
            metadata={"func": lambda rf: np.concatenate(rf.arrays["UT_yEnd"])},
        ),
        "ymin": pa.Column(
            pa.Float32,
            title="Strip y-min",
            description=(
                "The minimum y-coordinate of the hit, calculated "
                "as `min(ybegin, yend)`, in mm."
            ),
            metadata={"func": lambda rf: np.concatenate(rf.arrays["UT_yMin"])},
        ),
        "ymid": pa.Column(
            pa.Float32,
            title="Strip y-mid",
            description=(
                "The middle y-coordinate of the hit, "
                "calculated as the average of `ybegin` and `yend`, in mm."
            ),
            metadata={"func": lambda rf: np.concatenate(rf.arrays["UT_yMid"])},
        ),
        "ymax": pa.Column(
            pa.Float32,
            title="Strip y-max",
            description=(
                "The maximum y-coordinate of the hit, "
                "calculated as `max(ybegin, yend)`, in mm."
            ),
            metadata={"func": lambda rf: np.concatenate(rf.arrays["UT_yMax"])},
        ),
        "zateq0": pa.Column(
            pa.Float32,
            title="z-coordinate at y=0",
            description="The z-coordinate of the UT hit at y=0, in mm.",
            metadata={"func": lambda rf: np.concatenate(rf.arrays["UT_zAtYEq0"])},
        ),
        "run_id": RUN_ID_COLUMN,
        "event_id": EVENT_ID_COLUMN,
        "lhcb_id": add_metadata(
            LHCB_ID_COLUMN,
            {"func": lambda rf: np.concatenate(rf.arrays["UT_lhcbID"])},
        ),
        "particle_id": add_metadata(
            PARTICLE_ID_COLUMN,
            {"func": lambda rf: compute_particle_id(rf.arrays, "UT_lhcbID")},
        ),
    },
    title="UT hits-particles association",
    description=(
        "A dataframe of UT hit information where each row represents "
        "the association between a single hit and a single particle."
    ),
    strict=True,
    coerce=True,
    unique=["run_id", "event_id", "lhcb_id", "particle_id"],
)
