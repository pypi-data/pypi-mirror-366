"""Defines the step for ensuring a valid LHCb grid proxy is available."""

from __future__ import annotations

import sys
from logging import getLogger
from os import environ
from types import NoneType
from typing import TYPE_CHECKING

from .._utils.path import ResolvedPath  # noqa: TC001 (needed by Pydantic)
from ..core.step import StepKey, StepKind
from ..environment import execute
from .base import StepBase

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ..context import Context

__all__ = ["GenerateGridProxyStep"]

logger = getLogger(__name__)


class GenerateGridProxyStep(StepBase[None]):
    """Ensures a valid LHCb grid proxy is available.

    This step is typically used at the beginning of a workflow to check for and,
    if necessary, initialize a grid proxy. It runs an external script that
    handles the interactive password prompt.

    If the ``DIGOUT_BATCH_MODE`` environment variable is set to ``1``,
    the execution will be skipped, typically to skip the proxy generation
    in a non-interactive batch environment.
    """

    proxy_path: ResolvedPath | None = None
    """The file path where the grid proxy should be stored.

    If set, the ``X509_USER_PROXY`` environment variable will be set to this
    path before the proxy is initialized.
    """

    duration: str | None = None
    """The desired validity duration for the proxy (e.g., ``24:00``).

    If the proxy needs to be created, this value is passed to the underlying
    ``lhcb-proxy-init`` command. If not set, the command's default is used.
    """

    timeout: float | None = None
    """The maximum time to wait when checking the proxy status."""

    skip: bool = False
    """If ``True``, skip the grid proxy checking and initialization."""

    def _run(self, sources: Mapping[StepKey, object], _: Context, /) -> None:
        """Execute the proxy initialization script.

        This method sets the ``X509_USER_PROXY`` environment variable if a path
        is specified and then calls an external script responsible for checking
        and creating the proxy.
        """
        assert not sources
        if (proxy_path := self.proxy_path) is not None:
            environ["X509_USER_PROXY"] = proxy_path.as_posix()
            logger.info("Setting 'X509_USER_PROXY' to '%s'", proxy_path.as_posix())

        if self.skip:
            logger.info("Skipping grid proxy generation as 'skip' is set to True.")
            return
        else:
            args = [sys.executable, "-m", "digout.script._initialize_lhcb_proxy"]
            if self.duration:
                args.extend(["--duration", self.duration])
            if self.timeout is not None:
                args.extend(["--timeout", str(self.timeout)])
            execute(args)

    @classmethod
    def get_stream_type(cls) -> type:
        """Return ``NoneType``."""
        return NoneType

    @classmethod
    def get_chunk_type(cls) -> type:
        """Return ``NoneType``."""
        return NoneType

    @classmethod
    def get_key(cls) -> str:
        """Return the key for this step, ``generate_grid_proxy``."""
        return "generate_grid_proxy"

    @property
    def kind(self) -> StepKind:
        """:py:attr:`~digout.core.step.StepKind.STREAM`."""
        return StepKind.STREAM

    def _has_run(self, context: Context, /) -> bool:  # noqa: ARG002
        """Check if the step should be skipped.

        The step is skipped if the ``DIGOUT_BATCH_MODE`` environment variable
        is set to ``1``, or if the `skip` attribute is set to ``True``
        and there is not need to export the proxy path
        to the ``X509_USER_PROXY`` environment variable.
        """
        # Do not run this step if the batch mode is enabled.
        return (self.skip and self.proxy_path is None) or (
            environ.get("DIGOUT_BATCH_MODE") == "1"
        )

    def get_target(self, context: Context, /) -> None:  # noqa: ARG002
        """Return ``None`` as the target for this step."""
        return
