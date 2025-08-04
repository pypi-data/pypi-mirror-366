"""Module for loading and dumping YAML files.

This module provides functions to load and dump YAML files, with logging capabilities.
"""

from __future__ import annotations

from logging import getLogger
from pathlib import Path
from typing import Any

from yaml import safe_dump, safe_load

from .._utils.path import PathLike, create_directory

logger = getLogger(__name__)

__all__ = ["dump_yaml", "load_yaml"]


def load_yaml(path: PathLike) -> object:
    """Load a YAML file and return its content.

    This function also logs the path of the YAML file being loaded.

    Args:
        path: The path to the YAML file.

    Returns:
        The content of the YAML file as a Python object.
    """
    path = Path(path)
    logger.debug("Loading YAML file from '%s'", path)
    with path.open("r") as file:
        return safe_load(file)


def dump_yaml(data: object, path: PathLike, **kwargs: Any) -> None:
    """Dump a Python object to a YAML file.

    This function also logs the path where the YAML file is being saved.

    Args:
        data: The Python object to be dumped to YAML.
        path: The path where the YAML file will be saved.
        **kwargs: Additional keyword arguments to pass to :py:func:`yaml.safe_dump`.
            By default, ``sort_keys`` is set to ``False``.
    """
    path = Path(path)

    create_directory(path.parent)

    logger.debug("Dumping YAML file to '%s'", path)
    kwargs.setdefault("sort_keys", False)
    with path.open("w") as file:
        safe_dump(data, file, **kwargs)
