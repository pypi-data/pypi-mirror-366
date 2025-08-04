"""Defines an environment model for activating the LHCb DIRAC environment."""

from __future__ import annotations

import subprocess
from functools import lru_cache
from logging import getLogger
from typing import TYPE_CHECKING, Any, Literal

from pydantic import BaseModel

from .._utils.resources import get_lbenv_script

if TYPE_CHECKING:
    from collections.abc import Sequence

__all__ = ["DiracEnvironment"]

logger = getLogger(__name__)


def _get_available_versions() -> list[str]:
    """Retrieve all available DIRAC client versions.

    This function calls the ``lb-dirac --list`` command and parses its output.

    Returns:
        A list of available version strings.

    Raises:
        RuntimeError: If the ``lb-dirac`` command fails.
    """
    result = subprocess.run(  # noqa: S603
        [get_lbenv_script().as_posix(), "lb-dirac", "--list"],
        text=True,
        capture_output=True,
        check=False,
        stdout=None,
        stderr=None,
    )

    if result.returncode != 0:
        msg = f"Failed to get Dirac version: {result.stderr}"
        raise RuntimeError(msg)

    return result.stdout.splitlines()


@lru_cache
def _get_latest_version() -> str:
    """Retrieve the most recent available DIRAC client version.

    Returns:
        The latest version string.

    Raises:
        ValueError: If no versions can be found.
    """
    versions = _get_available_versions()
    logger.debug("Found %d Dirac versions", len(versions))
    if not versions:
        msg = "No Dirac versions found."
        raise ValueError(msg)

    return versions[0]


class DiracEnvironment(BaseModel):
    """A model for activating the LHCb DIRAC environment using ``lb-dirac``.

    This class wraps the ``lb-dirac`` command, which is necessary for running
    DIRAC client tools (e.g., ``dirac-proxy-info``). If no version is specified,
    it automatically discovers and uses the latest available one.
    """

    type: Literal["dirac"] = "dirac"
    """The discriminator field."""

    version: str | None = None
    """The DIRAC client version to activate.

    If left as ``None``, the latest available version will be automatically
    determined and used at runtime.
    """

    def model_post_init(self, _: Any, /) -> None:
        """Lazily populates the version if it was not provided."""
        if self.version is None:
            logger.debug(
                "No version specified for Dirac environment, "
                "Fetching the last available version for reproducibility.",
            )
            self.version = _get_latest_version()

    def get_args(self, args: Sequence[str]) -> list[str]:
        """Prepends the ``lb-dirac`` activation command to the given arguments.

        Args:
            args: The command-line arguments to execute within the DIRAC env.

        Returns:
            A new list of arguments prefixed with the ``lb-dirac`` command.

        Examples:
            >>> env = DiracEnvironment(version="v8r0p0")
            >>> env.get_args(["dirac-proxy-info", "--hours"])
            ['../digout/script/_source_lbenv.sh', 'lb-dirac', 'v8r0p0', 'dirac-proxy-info', '--hours']
        """  # noqa: E501
        logger.debug("Setting up Dirac environment with version: %s", self.version)
        env_args = [get_lbenv_script().as_posix(), "lb-dirac"]

        if self.version:
            env_args.append(self.version)

        return [*env_args, *args]
