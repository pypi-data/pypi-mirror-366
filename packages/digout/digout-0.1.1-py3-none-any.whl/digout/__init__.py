"""A wrapper around Moore or Allen programs."""

from os import environ

__version__ = "0.1.1"

# Set the DIGOUT_VERSION environment variable to the current version
environ["DIGOUT_VERSION"] = __version__

__all__ = ["__version__"]
