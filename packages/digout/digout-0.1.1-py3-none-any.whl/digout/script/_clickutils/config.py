"""A module containing Click options for configuration management."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from click.decorators import FC

_CLICK_CONFIG_PATH_ARGUMENT = click.argument(
    "config_paths",
    nargs=-1,
    type=click.Path(path_type=Path, exists=True, dir_okay=False),
)

_CLICK_OVERRIDES_OPTION = click.option(
    "-d",
    "--override",
    "overrides",
    default=[],
    type=str,
    multiple=True,
    metavar="<section>.<key>=<value>",
    help="Override a configuration value in the form '<section>.<key>=<value>'.",
)
"""A Click option to specify overrides for configuration values."""


def CLICK_CONFIG_OPTIONS(func: FC) -> FC:  # noqa: N802
    """A Click decorator to add configuration options to a command.

    This decorator adds options for specifying configuration files and overrides.
    It can be used to decorate Click commands that require configuration management.
    """  # noqa: D401
    return _CLICK_CONFIG_PATH_ARGUMENT(_CLICK_OVERRIDES_OPTION(func))
