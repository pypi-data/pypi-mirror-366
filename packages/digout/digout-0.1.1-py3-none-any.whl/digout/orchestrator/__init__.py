"""Provide orchestrator implementations for executing workflows.

This package contains different orchestrators, which are responsible for
controlling the execution of a workflow's dependency graph.

It also exposes a pre-populated :py:class:`~digout.registry.Registry` instance
containing these implementations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from ..registry import Registry
from .debug import DebugOrchestrator
from .simple import SimpleOrchestrator

if TYPE_CHECKING:
    from ..core.orchestrator import OrchestratorProtocol
    from ..registry._key import OrchestratorKey

__all__ = ["ORCHESTRATOR_REGISTRY"]


ORCHESTRATOR_REGISTRY: Final[Registry[OrchestratorKey, OrchestratorProtocol]] = (
    Registry(name="orchestrator", import_path=f"{__name__}.ORCHESTRATOR_REGISTRY")
)
"""A pre-populated registry of the orchestrators provided by this package.

This :py:class:`~digout.registry.Registry` instance contains the following
implementations:

- **"simple"**: :py:class:`.simple.SimpleOrchestrator` runs steps sequentially.
- **"debug"**: :py:class:`.debug.DebugOrchestrator` logs the execution plan
  without running any steps.
"""


ORCHESTRATOR_REGISTRY.register_many([SimpleOrchestrator, DebugOrchestrator])
