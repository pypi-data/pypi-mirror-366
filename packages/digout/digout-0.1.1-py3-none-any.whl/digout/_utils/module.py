"""Utility functions for importing objects dynamically."""

from __future__ import annotations

from importlib import import_module
from logging import getLogger

logger = getLogger(__name__)


__all__ = ["import_object"]


def import_object(name: str) -> object:
    """Import an object by its name.

    Args:
        name: The name of the object to import, in the format 'module.object'.

    Returns:
        The imported object.

    Raises:
        ValueError: If the name is not in the correct format.
        ImportError: If the module or object cannot be found.
    """
    module_name, _, object_name = name.rpartition(".")
    if not module_name or not object_name:
        msg = f"Invalid object name: {name}. Must be in the format 'module.object'."
        raise ValueError(msg)
    logger.debug("Importing object '%s' from module '%s'", object_name, module_name)
    module = import_module(module_name)
    try:
        return getattr(module, object_name)
    except AttributeError as e:
        msg = f"Object '{object_name}' not found in module '{module_name}'."
        raise ImportError(msg) from e
