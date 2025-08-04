"""Provides utilities for loading and merging YAML configurations using OmegaConf.

This module offers a flexible way to build a configuration from multiple YAML
files and command-line overrides. It uses ``omegaconf`` to handle merging,
variable interpolation, and conversion to standard Python objects.
"""

from __future__ import annotations

from collections.abc import Sequence
from logging import getLogger
from typing import TYPE_CHECKING, Any, Self

from omegaconf import DictConfig, OmegaConf
from pydantic import BaseModel

from .._utils.ioyaml import dump_yaml

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from .._utils.path import IOLike, PathLike


__all__ = ["ConfigError", "YAMLMixin", "read_config"]

logger = getLogger(__name__)


PRIVATE_PREFIX = "_"
"""Top-level keys in YAML files starting with this prefix will be ignored."""


class ConfigError(RuntimeError):
    """A custom error raised for issues during configuration loading or parsing."""


def _load_config(path: IOLike) -> DictConfig:
    """Load a single YAML file into an ``OmegaConf.DictConfig`` object.

    Args:
        path: The path to the YAML file to load.

    Raises:
        ConfigError: If the loaded configuration is not a dictionary-like object.
    """
    logger.info("Loading configuration from: %s", path)
    cfg = OmegaConf.load(path)
    if not isinstance(cfg, DictConfig):
        msg = f"Expected DictConfig from {path}, got {type(cfg)}.__name__"
        raise ConfigError(msg)
    return cfg


def read_config(
    config_paths: Sequence[IOLike] | None = None, overrides: Sequence[str] | None = None
) -> dict[Any, Any]:
    """Load and merge configurations from YAML files and command-line overrides.

    This function orchestrates the entire configuration loading process:
    1.  Loads a sequence of YAML files, with later files overriding earlier ones.
    2.  Applies command-line overrides (e.g., ``runtime.scheduler_key=local``).
    3.  Merges all sources into a single configuration tree.
    4.  Resolves any variable interpolations (e.g., ``${...}``).
    5.  Removes any top-level keys that start with an underscore.

    Args:
        config_paths: A sequence of paths to YAML configuration files.
        overrides: A sequence of dot-style override strings from the command line.

    Returns:
        A standard Python dictionary representing the final, resolved configuration.

    Raises:
        ConfigError: If merging fails or the configuration is malformed.
    """
    # 1. Load YAML files --------------------------------------------------
    configs = [_load_config(path) for path in config_paths] if config_paths else []

    # 2. Apply overrides -------------------------------------------------
    if overrides:
        overrides = list(overrides)
        logger.debug("Applying overrides: %s", overrides)
        configs.append(OmegaConf.from_dotlist(overrides))

    if not configs:
        logger.warning(
            "No configuration files or overrides provided. Using empty config."
        )
        return {}

    # 3. Merge configs ---------------------------------------------------
    config = OmegaConf.merge(*configs)
    if not isinstance(config, DictConfig):
        msg = f"Expected DictConfig after merging, got {type(config).__name__}"
        raise ConfigError(msg)

    # 4. Resolve interpolations ------------------------------------------
    config_dict = OmegaConf.to_object(config)
    if not isinstance(config_dict, dict):
        msg = (
            "Failed to convert DictConfig to a plain dict. "
            f"Got {type(config_dict).__name__}."
        )
        raise TypeError(msg)

    # 5. Strip private keys ----------------------------------------------
    return {
        k: v
        for k, v in config_dict.items()
        if not isinstance(k, str) or not k.startswith(PRIVATE_PREFIX)
    }


class YAMLMixin(BaseModel):
    """A Pydantic mixin for loading from and dumping to YAML format.

    Classes that inherit from this mixin gain :py:meth:`.create`
    and :py:meth:`.to_yaml`methods, enabling easy serialization and deserialization.
    """

    @classmethod
    def create(
        cls,
        config_paths: Sequence[IOLike] | None = None,
        overrides: Sequence[str] | None = None,
        **kwargs: Any,
    ) -> Self:
        """Create an instance of the class from YAML files and overrides.

        This factory method uses :py:func:`read_config` to load and merge all
        configuration sources and then validates the result against the Pydantic
        model.

        Args:
            config_paths: A sequence of paths to YAML configuration files.
            overrides: A sequence of dot-style override strings.
            **kwargs: Additional keyword arguments passed to
                ``pydantic.BaseModel.model_validate`` method.

        Returns:
            A new, validated instance of the class.
        """
        config_dict = read_config(config_paths, overrides)
        return cls.model_validate(config_dict, **kwargs)

    def to_yaml(
        self,
        path: PathLike,
        *,
        pydantic_kwargs: Mapping[str, Any] | None = None,
        yaml_kwargs: Mapping[str, Any] | None = None,
    ) -> None:
        """Save the Pydantic model instance to a YAML file.

        Args:
            path: The destination file path.
            pydantic_kwargs: Additional keyword arguments passed to Pydantic's
                ``pydantic.BaseModel.model_dump`` method
                (e.g., ``{"exclude": {"field_name"}}``).
            yaml_kwargs: Additional keyword arguments passed to the underlying
                YAML dumper.
        """
        return dump_yaml(
            self.model_dump(mode="json", **(pydantic_kwargs or {})),
            path,
            **(yaml_kwargs or {}),
        )
