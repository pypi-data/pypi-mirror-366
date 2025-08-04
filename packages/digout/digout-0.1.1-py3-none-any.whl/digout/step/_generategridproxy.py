"""Provides helper functions for managing an LHCb grid proxy.

This module contains functions that wrap the ``lhcb-proxy-info`` and
``lhcb-proxy-init`` command-line tools to check for and initialize a valid
grid proxy required for interacting with grid resources.
"""

from __future__ import annotations

import subprocess
from logging import getLogger

from .._utils.resources import get_lbenv_script

logger = getLogger(__name__)


def is_lhcb_proxy_enabled(timeout: float | None = None) -> bool:
    """Check if a valid LHCb grid proxy is currently active.

    This function executes the ``lhcb-proxy-info --checkvalid`` command to verify
    the existence and validity of the user's grid proxy.

    Args:
        timeout: The maximum time to wait for the command to complete.

    Returns:
        ``True`` if the proxy is valid. ``False`` if it is missing, has expired,
        or if an error occurs during the check.
    """
    # Check with the `lhcb-proxy-info` command
    try:
        result = subprocess.run(  # noqa: S603
            [get_lbenv_script().as_posix(), "lhcb-proxy-info", "--checkvalid"],
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as e:
        logger.warning("Timeout expired while checking LHCb proxy: %s", e)
        return False

    returncode = result.returncode
    if returncode == 0:
        logger.debug("LHCb proxy is enabled and valid.")
        return True
    elif returncode == 1:
        logger.info("LHCb proxy is not enabled or has expired.")
        logger.debug("Command output: %s", result.stdout)
        return False
    elif returncode == 127:
        logger.error(
            "The 'lhcb-proxy-info' command is not found. "
            "Please ensure you are in the LHCb environment."
        )
        return False
    else:
        logger.error(
            "Unexpected return code %d from 'lhcb-proxy-info': %s",
            returncode,
            result.stderr,
        )
        return False


def init_lhcb_proxy(duration: str | None) -> bool:
    """Initialize a new LHCb grid proxy, prompting the user for their password.

    This function executes the ``lhcb-proxy-init`` command, which will typically
    trigger an interactive password prompt in the user's terminal.

    Args:
        duration: The validity period for the new proxy, in ``HH:MM`` format.
            If ``None``, the command's default duration is used.

    Returns:
        ``True`` if the proxy was initialized successfully, ``False`` otherwise.
    """
    logger.info("Running 'lhcb-proxy-init' to initialize the LHCb proxy.")

    args = [get_lbenv_script().as_posix(), "lhcb-proxy-init"]
    if duration:
        args.extend(["--valid", duration])

    result = subprocess.run(  # noqa: S603
        args, check=False, capture_output=False, text=True
    )
    returncode = result.returncode
    if returncode == 0:
        logger.info("LHCb proxy initialized successfully.")
        return True
    elif returncode == 127:
        logger.error(
            "The 'lhcb-proxy-init' command is not found so that "
            "we cannot prompt you to initialize the LHCb proxy."
        )
        return False
    else:
        logger.error(
            "Failed to initialize LHCb proxy. Return code %d: %s",
            returncode,
            result.stderr,
        )
        return False
