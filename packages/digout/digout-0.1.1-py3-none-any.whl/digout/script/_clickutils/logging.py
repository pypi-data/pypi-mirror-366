"""Logging configuration for Click commands."""

from __future__ import annotations

import click

from ..._utils.logging import DEFAULT_LOG_LEVEL, LOG_LEVELS, setup_basic_logging

CLICK_LOGGING_OPTION = click.option(
    "-l",
    "--log-level",
    type=click.Choice(LOG_LEVELS),
    default=DEFAULT_LOG_LEVEL,
    help="Set the logging level.",
    is_eager=True,  # run this callback before other options
    expose_value=False,  # we don't need to inject `log_level` into the command
    callback=lambda ctx, param, value: setup_basic_logging(value),  # noqa: ARG005
    show_default=True,
)
