"""Provides functionality for initializing a project with default configuration files.

This module is used by the ``digout init`` command-line interface to copy
template configuration files into a user's project directory, helping to
bootstrap a new production workflow.
"""

from __future__ import annotations

from contextlib import contextmanager
from enum import StrEnum
from importlib.resources import as_file, files
from logging import INFO, getLogger
from pathlib import Path
from shutil import copy
from typing import TYPE_CHECKING

from .._utils.path import PathLike, create_directory

if TYPE_CHECKING:
    from collections.abc import Generator

__all__ = ["ConfType", "copy_init_config_files"]

logger = getLogger(__name__)


class ConfType(StrEnum):
    """An enumeration of the available configuration templates."""

    BASE = "base"
    """The base configuration files, common to all production runs."""

    PROD = "prod"
    """Example configuration for a specific production run."""


def _check_no_overwrite(destination_paths: list[Path], /) -> None:
    """Verify that none of the destination paths already exist.

    Args:
        destination_paths: A list of file paths to check.

    Raises:
        FileExistsError: If any of the specified paths already exist.
    """
    existing_destination_paths = [
        destination_path
        for destination_path in destination_paths
        if destination_path.exists()
    ]
    if existing_destination_paths:
        msg = "The following files would be overwritten: " + ", ".join(
            repr(target.as_posix()) for target in existing_destination_paths
        )
        raise FileExistsError(msg)


@contextmanager
def _get_init_config_files(conftype: ConfType) -> Generator[list[Path], None, None]:
    """Retrieve the paths of the packaged configuration template files.

    This context manager locates the specified configuration files within the
    ``digout.conf`` package resources, making them available as concrete file paths.

    Args:
        conftype: The type of configuration files to retrieve.

    Yields:
        A list of ``Path`` objects for the source configuration files.
    """
    with as_file(files("digout.conf").joinpath(conftype.value)) as conf_path:
        yield list(conf_path.iterdir())


def copy_init_config_files(
    conftype: ConfType, output_dir: PathLike, *, overwrite: bool = False
) -> None:
    """Copy a set of template configuration files to a specified directory.

    Args:
        conftype: The type of configuration template to copy.
        output_dir: The destination directory for the new files.
        overwrite: If ``True``, existing files with the same name will be
            overwritten. Defaults to ``False``.

    Raises:
        FileExistsError: If ``overwrite`` is ``False`` and any of the destination
            files already exist.
    """
    create_directory(output_dir)

    output_dir = Path(output_dir).expanduser().resolve()
    with _get_init_config_files(conftype) as source_paths:
        if logger.isEnabledFor(INFO):
            logger.info(
                "Copying to directory '%s' the following configuration files: %s",
                output_dir,
                ", ".join(repr(file.name) for file in source_paths),
            )

        destination_paths = [
            output_dir / config_file.name for config_file in source_paths
        ]
        if not overwrite:
            _check_no_overwrite(destination_paths)

        for source_path, dest_path in zip(source_paths, destination_paths, strict=True):
            copy(source_path, dest_path)
            logger.debug("Copied %s to %s", source_path, dest_path)
