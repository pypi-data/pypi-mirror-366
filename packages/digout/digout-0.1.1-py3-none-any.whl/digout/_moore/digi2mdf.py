###############################################################################
# (c) Copyright 2019 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict

__all__ = ["DIGI2MDFConfig"]


class DIGI2MDFConfig(BaseModel):
    """Configuration for the DIGI to MDF conversion."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    path: Path
    """Path to the output MDF file."""

    geometry_dir: Path | None = None
    """Directory containing the geometry files, if applicable."""

    with_retina_clusters: bool = True
    """Whether the input data contains retina clusters.

    This means that the retina clusters need to be properly decoded from the input data.
    """


if __name__ == "builtins":  # pragma: no cover
    # IF RUN THROUGH MOORE
    from os import environ

    from Allen.config import allen_non_event_data_config, run_allen_reconstruction
    from PyConf.Algorithms import VPRetinaFullClustering
    from RecoConf.config import Reconstruction
    from RecoConf.hlt1_allen import (
        combine_raw_banks_with_MC_data_for_standalone_Allen_checkers,
    )
    from RecoConf.legacy_rec_hlt1_tracking import (
        make_RetinaCluster_raw_bank,
        make_RetinaClusters,
        make_velo_full_clusters,
    )
    from RecoConf.mc_checking import tracker_dumper
    from RecoConf.options import options
    from yaml import safe_load

    yaml_path = Path(environ["DIGOUT_DIGI2MDF_CONFIG_YAML"])
    with yaml_path.open() as file:
        config = DIGI2MDFConfig.model_validate(safe_load(file))

    options.output_type = "MDF"
    options.output_file = config.path.as_posix()

    def _dump_mdf() -> Any:
        algs = combine_raw_banks_with_MC_data_for_standalone_Allen_checkers(
            output_file=config.path.as_posix()
        )
        return Reconstruction("write_mdf", algs)

    with allen_non_event_data_config.bind(
        dump_geometry=config.geometry_dir is not None,
        out_dir=config.geometry_dir.as_posix() if config.geometry_dir else None,
    ):
        if config.with_retina_clusters:
            with (
                make_RetinaClusters.bind(make_raw=make_RetinaCluster_raw_bank),
                make_velo_full_clusters.bind(make_full_cluster=VPRetinaFullClustering),
                tracker_dumper.bind(velo_hits=make_RetinaClusters),
            ):
                run_allen_reconstruction(options, _dump_mdf)
        else:
            run_allen_reconstruction(options, _dump_mdf)
