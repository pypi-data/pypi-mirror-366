"""Defines specialized type aliases for registry keys in the DIGOUT library.

While all registry keys are fundamentally strings, these type aliases are used
throughout the library to provide semantic context to improve readability.

The library distinguishes between the following key types:
- :py:class:`~digout.core.step.StepKey`: Used for identifying steps, streams,
  and chunks.
- :py:class:`OrchestratorKey`: Used for identifying orchestrators.
- :py:class:`SchedulerKey`: Used for identifying schedulers.
"""

from __future__ import annotations

from typing import TypeAlias

OrchestratorKey: TypeAlias = str
"""A type alias for the key identifying an orchestrator in a registry.

This alias clarifies that a string is being used as a unique identifier for an
orchestrator type within a ``Registry`` instance.
"""

SchedulerKey: TypeAlias = str
"""A type alias for the key identifying a scheduler in a registry.

This alias clarifies that a string is being used as a unique identifier for a
scheduler type within a ``Registry`` instance.
"""
