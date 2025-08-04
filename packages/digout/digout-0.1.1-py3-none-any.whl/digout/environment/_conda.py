"""Defines an environment model for activating an LHCb Conda environment."""

from __future__ import annotations

import subprocess
from functools import lru_cache
from logging import getLogger
from typing import TYPE_CHECKING, Any, Literal

from pydantic import BaseModel

from .._utils.resources import get_lbenv_script

if TYPE_CHECKING:
    from collections.abc import Sequence


__all__ = ["CondaEnvironment"]

logger = getLogger(__name__)


def _get_available_versions(name: str) -> list[str]:
    """Retrieve all available versions for a given Conda environment name.

    This function calls the ``lb-conda --list <name>`` command and parses its
    output. The versions are returned sorted from newest to oldest.

    Args:
        name: The name of the Conda environment (e.g., ``default``).

    Returns:
        A list of version strings, with the most recent version first.

    Raises:
        RuntimeError: If the ``lb-conda`` command fails.
    """
    result = subprocess.run(  # noqa: S603
        [get_lbenv_script().as_posix(), "lb-conda", "--list", name],
        text=True,
        capture_output=True,
        check=False,
        stdout=None,
        stderr=None,
    )

    if result.returncode != 0:
        msg = f"Failed to get Conda versions for '{name}': {result.stderr}"
        raise RuntimeError(msg)

    versions = result.stdout.splitlines()
    versions.reverse()  # Reverse to have the most recent version first
    return versions


@lru_cache
def _get_latest_version(name: str) -> str:
    """Retrieve the most recent version for a given Conda environment name.

    Args:
        name: The name of the Conda environment.

    Returns:
        The latest version string.

    Raises:
        ValueError: If no versions can be found for the given name.
    """
    versions = _get_available_versions(name)
    logger.debug("Found %d Conda versions for '%s'", len(versions), name)
    if not versions:
        msg = f"No Conda versions found for '{name}'."
        raise ValueError(msg)
    return versions[0]


class CondaEnvironment(BaseModel):
    """A model for activating an LHCb Conda environment using ``lb-conda``.

    This class wraps the ``lb-conda`` command, allowing other scripts to execute
    commands within a specified Conda environment and version. If no version is
    provided, it automatically discovers and uses the latest available one.
    """

    type: Literal["conda"] = "conda"
    """The discriminator field."""

    name: str = "default"
    """The name of the Conda environment to activate."""

    version: str | None = None
    """The version of the Conda environment.

    If left as ``None``, the latest available version for the given :py:attr:`name`
    will be automatically determined and used at runtime.
    """

    def model_post_init(self, _: Any, /) -> None:
        """Lazily populates the :py:attr:`version` if it was not provided."""
        if self.version is None:
            logger.debug(
                "No version specified for Conda environment '%s'. "
                "Fetching the last available version for reproducibility.",
                self.name,
            )
            self.version = _get_latest_version(self.name)

    @property
    def full_name(self) -> str:
        """Returns the full environment name in ``name/version`` format."""
        return f"{self.name}/{self.version}" if self.version else self.name

    def get_args(self, args: Sequence[str]) -> list[str]:
        """Prepend the ``lb-conda`` activation command to the given arguments.

        Args:
            args: The command-line arguments to execute.

        Returns:
            A new list of arguments prefixed with the ``lb-conda`` command.

        Examples:
            >>> env = CondaEnvironment(name="analysis-env", version="2025-02-19")
            >>> env.get_args(["python", "-c", "print(42)"])
            ['../digout/script/_source_lbenv.sh', 'lb-conda', 'analysis-env/2025-02-19', 'python', '-c', 'print(42)']
        """  # noqa: E501
        logger.debug("Setting up Conda environment with name: %s", self.full_name)
        return [get_lbenv_script().as_posix(), "lb-conda", self.full_name, *args]
