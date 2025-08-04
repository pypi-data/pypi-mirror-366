#!/usr/bin/env python3
"""A script that initializes the LHCb proxy if it is not already initialized.

This is a simple wrapper around the `lhcb-proxy-init` and `lhcb-proxy-info` commands.
"""

from __future__ import annotations

import sys
from logging import getLogger

import click

from ._clickutils import CLICK_LOGGING_OPTION

logger = getLogger(__name__)


@click.command()
@click.option(
    "-d",
    "--duration",
    default=None,
    help=(
        "The duration for which the proxy should be valid, in the format 'HH:MM'. "
        "If not specified, the default duration will be used."
    ),
    show_default=False,
    type=str,
    required=False,
)
@click.option(
    "-t",
    "--timeout",
    required=False,
    default=None,
    type=float,
    help=(
        "The maximum time to wait when checking the proxy status. "
        "If not specified, No timeout will be applied."
    ),
)
@CLICK_LOGGING_OPTION
def initialize_lhcb_proxy(duration: str | None, timeout: float | None) -> None:
    """Initialize the LHCb proxy if it is not already initialized."""
    from ..step._generategridproxy import is_lhcb_proxy_enabled  # noqa: PLC0415

    if is_lhcb_proxy_enabled(timeout=timeout):
        logger.info("LHCb proxy is already enabled.")
    else:
        logger.info("LHCb proxy is not enabled. Initializing...")
        from ..step._generategridproxy import init_lhcb_proxy  # noqa: PLC0415

        if not init_lhcb_proxy(duration):
            logger.error(
                "Failed to initialize LHCb proxy. Please check your environment "
                "and ensure that the 'lhcb-proxy-init' command is available."
            )
            sys.exit(1)


if __name__ == "__main__":
    initialize_lhcb_proxy()
