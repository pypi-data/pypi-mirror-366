"""Path utilities."""

from __future__ import annotations

import shutil
from logging import getLogger
from pathlib import Path
from tempfile import gettempdir
from typing import IO, Annotated, Any, TypeAlias
from uuid import uuid4

from pydantic import BeforeValidator

logger = getLogger(__name__)

__all__ = [
    "IOLike",
    "PathLike",
    "create_directory",
    "directory_not_empty",
    "get_temporary_path",
    "remove_directory",
    "remove_file",
]

PathLike: TypeAlias = str | Path
"""Type alias for path-like objects."""

IOLike: TypeAlias = PathLike | IO[Any]
"""Type alias for objects that can be used as input/output paths."""

ResolvedPath = Annotated[
    Path, BeforeValidator(lambda v: Path(v).expanduser().resolve())
]
"""A Pydantic type that resolves a path to its absolute form."""


def get_temporary_path(prefix: str, suffix: str) -> Path:
    """Get a random temporary path.

    Args:
        prefix: The prefix for the temporary file name.
        suffix: The suffix for the temporary file name.

    Returns:
        A Path object representing the temporary file
        with a random name generated using uuid4.
    """
    temp_dir = Path(gettempdir())
    random_name = uuid4().hex
    return temp_dir / f"{prefix}{random_name}{suffix}"


def get_src_path() -> Path:
    """Get the path to the source directory."""
    return Path(__file__).resolve().parent.parent.parent


def copy_file(src: PathLike, dst: PathLike) -> None:
    """Copy a file from source to destination.

    Args:
        src: The source file path.
        dst: The destination file path.
    """
    create_directory(Path(dst).parent)
    shutil.copy(src, dst)
    logger.debug("Copied file from '%s' to '%s'", src, dst)


def create_directory(path: PathLike) -> None:
    """Create a directory if it does not exist.

    This function creates a directory and logs the action.

    Args:
        path: The path to the directory to create.

    Returns:
        The Path object representing the created directory.
    """
    dir_path = Path(path)
    if not dir_path.exists():
        dir_path.mkdir(parents=True, exist_ok=False)
        logger.debug("Created directory: %s", dir_path)


def remove_file(path: PathLike) -> None:
    """Remove a file if it exists.

    If the directory gets empty after removing the file,
    the directory is also removed.

    Args:
        path: The path to the file to remove.
    """
    file_path = Path(path)
    if file_path.exists():
        file_path.unlink(missing_ok=True)
        logger.debug("Removed file: %s", file_path)

        # Remove the parent directory if it is empty
        if not any(file_path.parent.iterdir()):
            file_path.parent.rmdir()
            logger.debug("Removed empty directory: %s", file_path.parent)


def remove_directory(path: PathLike) -> None:
    """Remove an empty or non-empty directory if it exists.

    Args:
        path: The path to the directory to remove.
    """
    dir_path = Path(path)
    if dir_path.exists():
        shutil.rmtree(dir_path, ignore_errors=True)
        logger.debug("Removed directory: %s", dir_path)
    else:
        logger.debug("Directory does not exist: %s", dir_path)


def directory_not_empty(path: PathLike) -> bool:
    """Check if a directory is not empty.

    Args:
        path: The path to the directory to check.

    Returns:
        True if the directory is not empty, False otherwise.
    """
    dir_path = Path(path)
    return any(dir_path.iterdir())
