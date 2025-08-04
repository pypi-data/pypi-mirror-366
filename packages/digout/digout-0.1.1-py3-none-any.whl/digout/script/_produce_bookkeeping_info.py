#!/usr/bin/env python3
"""Produce a JSON file with LHCb bookkeeping and production information.

This script queries the LHCb Bookkeeping system to retrieve information about
the logical file names (LFNs) and productions associated with a given
Bookkeeping path. It then formats this information into a JSON file.
"""

from __future__ import annotations

from logging import getLogger
from pathlib import Path

import click

from .._utils.ioyaml import dump_yaml
from ._clickutils import CLICK_LOGGING_OPTION

logger = getLogger(__name__)


@click.command()
@click.argument("bk_path", type=str, required=True)
@click.argument("output_path", type=Path, required=True)
@CLICK_LOGGING_OPTION
def produce_dirac_info(bk_path: str, output_path: Path) -> None:
    """Produce a YAML file with LHCb bookkeeping and production information.

    The first argument is the path to the LHCb Bookkeeping
    (e.g., /lhcb/MC/2012/ALLSTREAMS.DST/).
    The second argument is the output path for the YAML file.
    """
    from ..bookkeeping._dirac import get_bk_info_from_bk_path  # noqa: PLC0415

    output_path = output_path.expanduser().resolve()
    if not (parent_dir := output_path.parent).exists():
        logger.info("Creating directory: %s", parent_dir)
        parent_dir.mkdir(parents=True, exist_ok=False)

    logger.info("Producing LHCb Bookkeeping information for path: %s", bk_path)
    bk_info = get_bk_info_from_bk_path(bk_path)

    dump_yaml(bk_info.model_dump(mode="json"), output_path)


if __name__ == "__main__":
    produce_dirac_info()
