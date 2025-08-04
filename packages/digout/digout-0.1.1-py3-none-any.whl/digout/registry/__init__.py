"""Provide the core components for type registration and instantiation.

This package contains the ``Registry`` class, a Pydantic-aware mapping that
stores Python types under unique string keys. This mechanism allows components
like steps, orchestrators, and schedulers to be defined in configuration files
and instantiated at runtime.

The components made available by this package are:

- :py:class:`Registry`: The main class for mapping keys to types.
- :py:class:`WithKeyProtocol`: An interface for classes that can provide their
  own registration key.
- :py:class:`Registries`: A ``TypedDict`` for type-hinting a dictionary that
  holds step, stream, chunk, orchestrator, and scheduler registries.
- :py:data:`OrchestratorKey` and :py:data:`SchedulerKey`: Type aliases that
  provide semantic meaning for specific kinds of registry keys.
"""

from __future__ import annotations

from ._key import OrchestratorKey, SchedulerKey
from ._registries import Registries
from ._registry import Registry, WithKeyProtocol

__all__ = [  # noqa: RUF022
    "Registry",
    "WithKeyProtocol",
    "OrchestratorKey",
    "SchedulerKey",
    "Registries",
]
