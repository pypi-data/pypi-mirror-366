"""Define an environment model for activating an LHCb project with ``lb-run``."""

from __future__ import annotations

import re
import subprocess
from functools import lru_cache
from logging import getLogger
from typing import TYPE_CHECKING, Any, Literal

from pydantic import BaseModel

from .._utils.resources import get_lbenv_script

if TYPE_CHECKING:
    from collections.abc import Sequence


__all__ = ["RunEnvironment"]

logger = getLogger(__name__)


# ``lb-run --list <name>`` emits lines like:
#   v35r0p1   in /cvmfs/lhcb.cern.ch/lib/.../Gaudi/v35r0p1
# We grab the token before the first whitespace.
_VERSION_RE = re.compile(r"^(\S+)\s+in\b")


def _get_available_versions(name: str) -> list[str]:
    """Retrieve all available versions for a given LHCb project name.

    This function calls the ``lb-run --list <name>`` command and parses its
    output. The versions are returned sorted from newest to oldest.

    Args:
        name: The name of the LHCb project (e.g., ``Gaudi``, ``Moore``).

    Returns:
        A list of version strings, with the most recent version first.

    Raises:
        RuntimeError: If the ``lb-run`` command fails.
    """
    result = subprocess.run(  # noqa: S603
        [get_lbenv_script().as_posix(), "lb-run", "--list", name],
        text=True,
        capture_output=True,
        check=False,
        stdout=None,
        stderr=None,
    )
    if result.returncode != 0:
        msg = f"Failed to list versions for '{name}': {result.stderr.strip()}"
        raise RuntimeError(msg)

    return [
        m.group(1)
        for line in result.stdout.splitlines()
        if (m := _VERSION_RE.match(line))
    ]


@lru_cache
def _get_latest_version(name: str) -> str:
    """Retrieve the most recent version for a given LHCb project name.

    Args:
        name: The name of the LHCb project.

    Returns:
        The latest version string.

    Raises:
        ValueError: If no versions can be found for the given name.
    """
    versions = _get_available_versions(name)
    logger.debug("Found %d versions for '%s'", len(versions), name)
    if not versions:
        msg = f"No versions found for '{name}'."
        raise ValueError(msg)
    return versions[0]


class RunEnvironment(BaseModel):
    """A model for activating an LHCb project environment using ``lb-run``.

    This class wraps the ``lb-run`` command, which is typically used to access
    pre-compiled software like Moore or Gaudi from CVMFS without needing a local
    compilation. If no version is specified, it automatically uses the latest one.
    """

    type: Literal["run"] = "run"
    """The discriminator field."""

    name: str
    """The name of the LHCb project to activate (e.g., ``Moore``)."""

    version: str | None = None
    """The version of the project to activate (e.g., ``v55r5``).

    If left as ``None``, the latest available version for the given ``name`` will
    be automatically determined and used at runtime.
    """

    platform: str | None = None
    """An optional platform specifier (e.g., ``x86_64-centos7-gcc11-opt``)."""

    def model_post_init(self, _: Any, /) -> None:
        """Lazily populates the version if it was not provided."""
        if self.version is None:
            logger.debug(
                "No version specified for LHCb environment '%s', "
                "using the last available version",
                self.name,
            )
            self.version = _get_latest_version(self.name)
            logger.debug(
                "Using last available version '%s' for LHCb environment '%s'",
                self.version,
                self.name,
            )

    @property
    def full_name(self) -> str:
        """Return the full project name in ``name/version`` format."""
        return f"{self.name}/{self.version}" if self.version else self.name

    def get_args(self, args: Sequence[str]) -> list[str]:
        """Prepend the ``lb-run`` activation command to the given arguments.

        Args:
            args: The command-line arguments to execute.

        Returns:
            A new list of arguments prefixed with the ``lb-run`` command.

        Examples:
            >>> env = RunEnvironment(name="Moore", version="v55r5")
            >>> env.get_args(["gaudirun.py", "options.py"])
            ['../digout/script/_source_lbenv.sh', 'lb-run', 'Moore/v55r5', 'gaudirun.py', 'options.py']
        """  # noqa: E501
        env_args = [get_lbenv_script().as_posix(), "lb-run"]

        if self.platform:
            env_args.append(f"--platform={self.platform}")

        env_args.append(self.full_name)

        return [*env_args, *args]
