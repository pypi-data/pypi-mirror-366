"""Module for handling environment variables.

It provides logging and error handling for retrieving environment variables.
"""

from __future__ import annotations

import os
from logging import getLogger
from typing import Any

logger = getLogger(__name__)

__all__ = ["get_updated_environ"]


def get_updated_environ(**kwargs: Any) -> dict[str, str]:
    """Get all environment variables, and add those specified in kwargs.

    Args:
        **kwargs: Additional environment variables to retrieve.

    Returns:
        A dictionary all the environment variables, including those specified in kwargs.
    """
    env_vars = os.environ.copy()
    env_vars.update(kwargs)
    return env_vars
