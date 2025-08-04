"""Define the Pandera schema for the Monte Carlo particle dataframe."""

from __future__ import annotations

import numpy as np
import pandera.pandas as pa

from ._base import EVENT_ID_COLUMN, PARTICLE_ID_COLUMN, RUN_ID_COLUMN, add_metadata

PARTICLES_SCHEMA = pa.DataFrameSchema(
    columns={
        "n_velo_hits": pa.Column(
            pa.Int32,
            checks=pa.Check.ge(0),
            title="Number of Velo hits",
            description=(
                "The number of Velo detector hits associated with the particle."
            ),
            metadata={"func": lambda rf: rf.arrays["nbHits_in_Velo"][:-1]},
        ),
        "n_scifi_hits": pa.Column(
            pa.Int32,
            checks=pa.Check.ge(0),
            title="Number of SciFi hits",
            description=(
                "The number of SciFi detector hits associated with the particle."
            ),
            metadata={"func": lambda rf: rf.arrays["nbHits_in_SciFi"][:-1]},
        ),
        "n_ut_hits": pa.Column(
            pa.Int32,
            checks=pa.Check.ge(0),
            title="Number of UT hits",
            description="The number of UT detector hits associated with the particle.",
            metadata={"func": lambda rf: rf.arrays["nbHits_in_UT"][:-1]},
        ),
        "full_info": pa.Column(
            pa.Bool,
            title="Full info",
            description="A flag indicating if the particle has full information.",
            metadata={"func": lambda rf: rf.arrays["fullInfo"][:-1]},
        ),
        "has_velo": pa.Column(
            pa.Bool,
            title="Velo reconstructible",
            description=(
                "A flag indicating if the particle is reconstructible "
                "in the Velo detector."
            ),
            metadata={"func": lambda rf: rf.arrays["hasVelo"][:-1]},
        ),
        "has_scifi": pa.Column(
            pa.Bool,
            title="SciFi reconstructible",
            description=(
                "A flag indicating if the particle is reconstructible "
                "in the SciFi detector."
            ),
            metadata={"func": lambda rf: rf.arrays["hasSciFi"][:-1]},
        ),
        "has_ut": pa.Column(
            pa.Bool,
            title="UT reconstructible",
            description=(
                "A flag indicating if the particle is reconstructible "
                "in the UT detector."
            ),
            metadata={"func": lambda rf: rf.arrays["hasUT"][:-1]},
        ),
        "is_down": pa.Column(
            pa.Bool,
            title="Downstream particle",
            description=(
                "A flag for downstream particles (reconstructible in UT and SciFi)."
            ),
            metadata={"func": lambda rf: rf.arrays["isDown"][:-1]},
        ),
        "is_down_no_velo": pa.Column(
            pa.Bool,
            title="Downstream particle without Velo",
            description=(
                "A flag for downstream particles that are not reconstructible "
                "in the Velo."
            ),
            metadata={"func": lambda rf: rf.arrays["isDown_noVelo"][:-1]},
        ),
        "is_long": pa.Column(
            pa.Bool,
            title="Long particle",
            description=(
                "A flag for long particles (reconstructible in Velo and SciFi)."
            ),
            metadata={"func": lambda rf: rf.arrays["isLong"][:-1]},
        ),
        "is_long_and_ut": pa.Column(
            pa.Bool,
            title="Long particle with UT",
            description=(
                "A flag for long particles that are also reconstructible in the UT."
            ),
            metadata={"func": lambda rf: rf.arrays["isLong_andUT"][:-1]},
        ),
        "p": pa.Column(
            pa.Float64,
            checks=pa.Check.ge(0),
            title="Particle momentum",
            description="The magnitude of the particle's momentum vector, in MeV/c.",
            metadata={"func": lambda rf: rf.arrays["p"][:-1]},
        ),
        "pt": pa.Column(
            pa.Float64,
            checks=pa.Check.ge(0),
            title="Particle transverse momentum",
            description=(
                "The transverse component of the particle's momentum vector "
                "(perpendicular to the beam line), in MeV/c."
            ),
            metadata={"func": lambda rf: rf.arrays["pt"][:-1]},
        ),
        "eta": pa.Column(
            pa.Float64,
            title="Particle pseudorapidity",
            description=(
                "The pseudorapidity of the particle, defined as ``-ln(tan(theta/2))``, "
                "where theta is the polar angle."
            ),
            metadata={"func": lambda rf: rf.arrays["eta"][:-1]},
        ),
        "phi": pa.Column(
            pa.Float64,
            title="Particle azimuthal angle",
            description=(
                "The azimuthal angle of the particle's momentum vector "
                "in the plane perpendicular to the beam line, in radians."
            ),
            metadata={"func": lambda rf: rf.arrays["phi"][:-1]},
        ),
        "pid": pa.Column(
            pa.Int32,
            title="Monte Carlo Particle Number",
            description="The Particle Data Group (PDG) identifier for the particle.",
            metadata={"func": lambda rf: rf.arrays["pid"][:-1]},
        ),
        "from_beauty_decay": pa.Column(
            pa.Bool,
            title="From beauty decay",
            description=(
                "A flag indicating if any direct or indirect mother "
                "of this particle is a beauty hadron (B meson or baryon)."
            ),
            metadata={"func": lambda rf: rf.arrays["fromBeautyDecay"][:-1]},
        ),
        "from_charm_decay": pa.Column(
            pa.Bool,
            title="From charm decay",
            description=(
                "A flag indicating if any direct or indirect mother of this particle "
                "is a charm hadron (D meson or baryon)."
            ),
            metadata={"func": lambda rf: rf.arrays["fromCharmDecay"][:-1]},
        ),
        "from_strange_decay": pa.Column(
            pa.Bool,
            title="From strange decay",
            description=(
                "A flag indicating if the particle originates "
                "from a strange hadron decay. "
                "True if the direct mother has pid "
                "130 (K0L), 310 (K0S), 3122 (Lambda), 3222 (Sigma+), "
                "3212 (Sigma0), 3112 (Sigma-), 3322 (Xsi0), 3312 (Xsi-) "
                "or 3334 (Omega-), and if its origin vertex is within 5 mm "
                "of the beam line."
            ),
            metadata={"func": lambda rf: rf.arrays["fromStrangeDecay"][:-1]},
        ),
        "mother_pid": pa.Column(
            pa.Int32,
            title="Mother Monte Carlo Particle Number",
            description=(
                "The PDG ID of the direct mother particle. "
                "This is set to 0 if the particle has no mother."
            ),
            metadata={
                "func": lambda rf: np.where(
                    (mother_pid := rf.arrays["DecayOriginMother_pid"][:-1]) == -999999,
                    0,
                    mother_pid,
                )
            },
        ),
        "mother_key": pa.Column(
            pa.Int32,
            checks=pa.Check.ge(0),
            nullable=True,
            title="Mother Monte Carlo Particle ID",
            description=(
                "The particle ID (from the `particle_id` column) of the direct mother. "
                "This is set to 0 if the particle has no mother."
            ),
            metadata={
                "func": lambda rf: np.where(
                    (mother_key := rf.arrays["DecayOriginMother_key"][:-1]) == -999999,
                    0,
                    mother_key + 1,
                )
            },
        ),
        "mother_pt": pa.Column(
            pa.Float32,
            checks=pa.Check.ge(0),
            nullable=True,
            title="Mother Particle Transverse Momentum",
            description=(
                "The transverse momentum of the mother particle, in MeV/c. "
                "Set to NaN if there is no mother."
            ),
            metadata={
                "func": lambda rf: np.where(
                    # A value of -1 indicates that the mother particle is not available
                    # we use < 0.0 to avoid floating point issues
                    (mother_pt := rf.arrays["DecayOriginMother_pt"][:-1]) < 0.0,
                    np.nan,
                    mother_pt,
                )
            },
        ),
        "mother_tau": pa.Column(
            pa.Float32,
            checks=pa.Check.ge(0),
            nullable=True,
            title="Mother Particle Lifetime",
            description=(
                "The lifetime of the mother particle, in ns. "
                "Set to NaN if there is no mother."
            ),
            metadata={
                "func": lambda rf: np.where(
                    # A value of -1 indicates that the mother particle is not available
                    # we use < 0.0 to avoid floating point issues
                    (mother_tau := rf.arrays["DecayOriginMother_tau"][:-1]) < 0.0,
                    np.nan,
                    mother_tau,
                )
            },
        ),
        "ovtx_x": pa.Column(
            pa.Float64,
            title="Vertex x-coordinate",
            description="The x-coordinate of the particle's creation vertex, in mm.",
            metadata={"func": lambda rf: rf.arrays["ovtx_x"][:-1]},
        ),
        "ovtx_y": pa.Column(
            pa.Float64,
            title="Vertex y-coordinate",
            description="The y-coordinate of the particle's creation vertex, in mm.",
            metadata={"func": lambda rf: rf.arrays["ovtx_y"][:-1]},
        ),
        "ovtx_z": pa.Column(
            pa.Float64,
            title="Vertex z-coordinate",
            description="The z-coordinate of the particle's creation vertex, in mm.",
            metadata={"func": lambda rf: rf.arrays["ovtx_z"][:-1]},
        ),
        "run_id": RUN_ID_COLUMN,
        "event_id": EVENT_ID_COLUMN,
        "particle_id": add_metadata(
            PARTICLE_ID_COLUMN, {"func": lambda rf: rf.arrays["key"][:-1] + 1}
        ),
    },
    title="Particles",
    description=(
        "A dataframe of particle information, where each row represents "
        "a single particle."
    ),
    unique=["run_id", "event_id", "particle_id"],
    strict=True,
    coerce=True,
)
