"""Provides scheduler implementations for running chunked workflows.

This package contains various :py:class:`~digout.core.scheduler.SchedulerProtocol`
implementations, which control how a workflow is
executed across its different chunks
(e.g., in parallel on a local machine or on a remote batch system).

It also exposes a pre-populated :py:class:`~digout.registry.Registry` instance,
:py:data:`SCHEDULER_REGISTRY`, which contains all the schedulers defined
in this package.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..registry import Registry
from .debug import DebugScheduler
from .htcondor import HTCondorScheduler
from .local import LocalScheduler
from .simple import SimpleScheduler

if TYPE_CHECKING:
    from ..core.scheduler import SchedulerProtocol
    from ..registry._key import SchedulerKey

__all__ = ["SCHEDULER_REGISTRY"]


SCHEDULER_REGISTRY: Registry[SchedulerKey, SchedulerProtocol] = Registry(
    name="scheduler", import_path=f"{__name__}.SCHEDULER_REGISTRY"
)
"""A pre-populated registry of the schedulers provided by this package.

This :py:class:`~digout.registry.Registry` instance contains the following
implementations:

- **"simple"**: :py:class:`.simple.SimpleScheduler` runs chunks in parallel
  in memory without serializing the workflow.
- **"local"**: :py:class:`.local.LocalScheduler` serializes the workflow to a
  file and runs chunks in parallel using local subprocesses.
- **"htcondor"**: :py:class:`.htcondor.HTCondorScheduler` submits jobs for
  each chunk to an HTCondor cluster.
- **"debug"**: :py:class:`.debug.DebugScheduler` inspects the workflow and
  logs what would be run without any execution.
"""


SCHEDULER_REGISTRY.register_many(
    [LocalScheduler, SimpleScheduler, HTCondorScheduler, DebugScheduler]
)
