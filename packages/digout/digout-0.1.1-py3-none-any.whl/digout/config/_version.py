"""Provides a Pydantic mixin for tracking the library version in configurations."""

from __future__ import annotations

from logging import getLogger
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field

__all__ = ["VersionMixin"]

logger = getLogger(__name__)


def _get_wrapper_version() -> str:
    """Retrieve the current installed version of the ``digout`` package."""
    from digout import __version__  # noqa: PLC0415

    return __version__


def _log_version_mismatch(config_version: str) -> str:
    """Log a warning if versions are inconsistent.

    This function compares the version specified in a configuration file with
    the currently installed version of the library.

    Args:
        config_version: The version string from the configuration file.

    Returns:
        The ``config_version``, unchanged.
    """
    expected_version = _get_wrapper_version()
    if config_version != expected_version:
        logger.warning(
            "The version of the DIGOUT package (%s) does not match the expected "
            "version (%s). This may lead to unexpected behavior.",
            config_version,
            expected_version,
        )

    return config_version


class VersionMixin(BaseModel):
    """A Pydantic mixin to embed and check the ``digout`` version in a model.

    When a model with this mixin is created, it automatically stores the current
    library version. When it is loaded from a configuration, it checks if the
    version in the configuration matches the installed library version and logs
    a warning if they differ.
    """

    digout_version: Annotated[str, BeforeValidator(_log_version_mismatch)] = Field(
        default_factory=_get_wrapper_version
    )
    """The version of the ``digout`` library used to create this configuration.

    This field is automatically populated with the current library version upon
    model creation. When loading a configuration, it is used to detect potential
    incompatibilities between the configuration file and the installed code.
    """
