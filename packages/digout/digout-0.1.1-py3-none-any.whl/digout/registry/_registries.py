"""Define a ``TypedDict`` for a collection of component registries.

This module provides the `Registries` type, which is a `TypedDict` that defines
which serves as a formal type hint
for the dictionary of registries used throughout the ``digout`` framework, most
notably within the :py:class:`~digout.core.context.Context` class.
"""

from typing import Generic

from typing_extensions import TypedDict

from ..core.orchestrator import OrchestratorProtocol
from ..core.scheduler import SchedulerProtocol
from ..core.step import C_contra, StepKey, StepProtocol
from ._key import OrchestratorKey, SchedulerKey
from ._registry import Registry


class Registries(TypedDict, Generic[C_contra], total=False):
    """Defines the dictionary of registries used in the DIGOUT framework.

    As ``total=False``, a dictionary is not required to contain all keys.
    """

    step: Registry[StepKey, StepProtocol[C_contra, object]]
    """A registry for :py:class:`~digout.core.step.StepProtocol` implementations, keyed by :py:class:`~digout.core.step.StepKey`.

    A pre-populated instance is available at :py:data:`digout.step.STEP_REGISTRY`.
    """  # noqa: E501

    stream: Registry[StepKey, object]
    """A registry for stream types, keyed by :py:data:`~digout.core.step.StepKey`.

    A stream may implement the :py:class:`~digout.core.step.StepProtocol` interface
    so that it can be divided into chunks.

    A pre-populated instance is available at :py:data:`digout.step.STREAM_REGISTRY`.
    """

    chunk: Registry[StepKey, object]
    """A registry for chunk types, keyed by :py:data:`~digout.core.step.StepKey`.

    A pre-populated instance is available at :py:data:`digout.step.CHUNK_REGISTRY`.
    """

    orchestrator: Registry[OrchestratorKey, OrchestratorProtocol]
    """A registry for :py:class:`~digout.core.orchestrator.OrchestratorProtocol` implementations, keyed by :py:data:`~digout.registry.OrchestratorKey`.

    A pre-populated instance is available at
    :py:data:`digout.orchestrator.ORCHESTRATOR_REGISTRY`.
    """  # noqa: E501

    scheduler: Registry[SchedulerKey, SchedulerProtocol]
    """A registry for :py:class:`~digout.core.scheduler.SchedulerProtocol` implementations, keyed by :py:data:`~digout.registry.SchedulerKey`.

    A pre-populated instance is available at
    :py:data:`digout.scheduler.SCHEDULER_REGISTRY`.
    """  # noqa: E501
