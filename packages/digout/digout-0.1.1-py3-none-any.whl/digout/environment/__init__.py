"""Environments.

This package contains Pydantic models that wrap LHCb command-line tools like
``lb-run``, ``lb-conda``, and ``lb-dirac``. These models allow external commands
to be executed within a properly configured and activated environment.

The main components exposed are:

* :py:class:`Environment`: A discriminated union for configuring any of the
  supported environments.
* :py:class:`EnvironmentProtocol`: An interface that all environment models
  implement, defining the contract for command execution.
* :py:func:`execute`: A helper function to run commands within a given
  environment.

Three concrete environment models are provided:

* :py:class:`RunEnvironment`: wraps the ``lb-run`` command.
* :py:class:`DiracEnvironment`: wraps the ``lb-dirac`` command.
* :py:class:`CondaEnvironment`: wraps the ``lb-conda`` command.

"""

from __future__ import annotations

from typing import Annotated

from pydantic import Discriminator

from ._base import EnvironmentProtocol, execute
from ._conda import CondaEnvironment
from ._dirac import DiracEnvironment
from ._run import RunEnvironment

Environment = Annotated[
    RunEnvironment | DiracEnvironment | CondaEnvironment,
    Discriminator("type"),
]
"""A discriminated union of all supported environment types.

This allows Pydantic to parse a configuration into the correct environment
model based on a ``type`` field. For example, in a YAML file:

.. code-block:: yaml

   environment:
     type: run
     name: Moore
     version: v55r5

This would be parsed as a :py:class:`RunEnvironment` instance.
"""


__all__ = [  # noqa: RUF022
    "EnvironmentProtocol",
    "CondaEnvironment",
    "DiracEnvironment",
    "RunEnvironment",
    "Environment",
    "execute",
]
