"""A simple Moore option Python file that sets the options from a YAML file."""

from __future__ import annotations

if __name__ == "builtins":  # pragma: no cover
    from logging import basicConfig, getLogger
    from os import environ
    from pathlib import Path

    from Moore import options
    from yaml import safe_load

    basicConfig(
        level="DEBUG",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = getLogger(__name__)

    # Load the configuration from the YAML file specified by the environment variable
    yaml_path = Path(environ["DIGOUT_MOORE_OPTIONS_YAML"])
    with yaml_path.open() as file:
        logger.debug("Loading Moore options from '%s'", yaml_path)
        config = safe_load(file)

    if not isinstance(config, dict):
        msg = f"Configuration file '{yaml_path}' must contain a dictionary."
        raise TypeError(msg)

    # set the options from the config
    for key, value in config.items():
        setattr(options, key, value)
        logger.debug("Set Moore option '%s' to '%s'", key, value)
