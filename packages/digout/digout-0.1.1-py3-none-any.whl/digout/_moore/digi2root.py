"""Run the ROOT dumper implemented in Allen.

This file is adapted from the option file used to produce the MDF files:
https://gitlab.cern.ch/lhcb/Moore/-/blob/master/Hlt/RecoConf/options/mdf_for_standalone_Allen.py.

It should be run through Moore along with ``options.py`` located in this directory.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict

__all__ = ["DIGI2ROOTConfig"]


class DIGI2ROOTConfig(BaseModel):
    """Configuration for the DIGI2ROOT algorithm.

    This class is used to define the configuration for the DIGI2ROOT algorithm,
    which is a Moore step that processes DIGI files and converts them to ROOT format.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    with_retina_clusters: bool = True
    """Whether the input data contains retina clusters.

    This means that the retina clusters need to be properly decoded from the input data.
    """

    output_dir: Path
    """Path to the directory where the output ROOT files will be saved.

    If not specified, a temporary directory will be created in the system's temporary
    directory.
    The directory will have a random name with the prefix 'digi2root_'.
    """


if __name__ == "builtins":  # pragma: no cover
    # IF RUN THROUGH MOORE"
    from logging import getLogger
    from os import environ

    from Allen.config import run_allen_reconstruction
    from Moore.streams import bank_types_for_detectors
    from PyConf.Algorithms import RawEventCombiner, VPRetinaFullClustering
    from PyConf.application import default_raw_event
    from RecoConf.config import Reconstruction
    from RecoConf.legacy_rec_hlt1_tracking import (
        make_RetinaCluster_raw_bank,
        make_RetinaClusters,
        make_velo_full_clusters,
    )
    from RecoConf.mc_checking import pv_dumper, tracker_dumper
    from RecoConf.options import options
    from yaml import safe_load

    logger = getLogger(__name__)

    yaml_path = Path(environ["DIGOUT_DIGI2ROOT_CONFIG_YAML"])
    with yaml_path.open() as file:
        logger.debug("Loading DIGI2ROOT configuration from '%s'", yaml_path)
        config = DIGI2ROOTConfig.model_validate(safe_load(file))

    config.output_dir.parent.mkdir(parents=True, exist_ok=True)

    def _dump_root() -> Any:
        """Return the algorithm to dump the ROOT file."""
        tracker_dumper_algo = tracker_dumper(
            root_output_dir=config.output_dir.as_posix(), dump_to_root=True
        )
        pv_dumper_algo = pv_dumper()

        detector_parts = [default_raw_event(bt) for bt in bank_types_for_detectors()]
        # get only unique elements while preserving order
        detector_parts = list(dict.fromkeys(detector_parts).keys())
        combiner = RawEventCombiner(
            RawEventLocations=[
                *detector_parts,
                tracker_dumper_algo.OutputRawEventLocation,
                pv_dumper_algo.OutputRawEventLocation,
            ],
        )
        algos = [tracker_dumper_algo, combiner]

        return Reconstruction("write_root", algos)

    if config.with_retina_clusters:
        with (
            make_RetinaClusters.bind(make_raw=make_RetinaCluster_raw_bank),
            make_velo_full_clusters.bind(make_full_cluster=VPRetinaFullClustering),
            tracker_dumper.bind(velo_hits=make_RetinaClusters),
        ):
            run_allen_reconstruction(options, _dump_root)
    else:
        run_allen_reconstruction(options, _dump_root)
