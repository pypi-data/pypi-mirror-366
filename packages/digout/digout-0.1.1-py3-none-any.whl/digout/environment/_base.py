"""Define the core protocol and execution function for environments.

This module provides two key components:

- :py:class:`EnvironmentProtocol`: An interface that defines the contract for any
  environment wrapper.
- :py:func:`execute`: A convenience function that wraps ``subprocess.run`` to execute
  a command, optionally within an environment that conforms to the protocol.
"""

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from collections.abc import Sequence
    from subprocess import CompletedProcess

logger = getLogger(__name__)

__all__ = ["EnvironmentProtocol", "execute"]


@runtime_checkable  # necessary for Pydantic that runs isinstance checks
class EnvironmentProtocol(Protocol):
    """An interface for environment wrappers.

    Any class that implements this protocol can be used to wrap a command-line
    process, prepending the necessary arguments to activate a specific runtime
    environment before the command is executed.
    """

    def get_args(self, args: Sequence[str]) -> list[str]:
        """Prepend environment activation arguments to a command.

        Args:
            args: The original command-line arguments to be executed (e.g.,
                ``["python", "-c", "print(42)"]``).

        Returns:
            A new list of arguments that includes the environment activation
            command (e.g.,
            ``["lb-run", "MyProject/v1r0", "--", "python", "-c", "print(42)"]``).
        """
        ...


def execute(
    args: Sequence[str], environment: EnvironmentProtocol | None = None, **kwargs: Any
) -> CompletedProcess[str]:
    """Execute a command, optionally within a specified environment.

    This function is a high-level wrapper around ``subprocess.run``. If an
    `environment` is provided, it first uses it to modify the command-line
    arguments before execution. It also sets safe defaults for ``subprocess.run``.

    Args:
        args: The command-line arguments to run.
        environment: An optional environment object. If provided, its
            :py:meth:`~EnvironmentProtocol.get_args` method is called to
            prepend activation arguments to the command.
        **kwargs: Additional keyword arguments forwarded to ``subprocess.run``.
            The following defaults are set if not provided:

            - ``text=True``: ensures stdout/stderr are strings.
            - ``check=True``: raises ``CalledProcessError`` on non-zero exit codes.
            - ``start_new_session=True``: runs the command in a new session.

    Returns:
        The ``CompletedProcess`` object returned by ``subprocess.run``.

    Examples:
        Execute a simple command:

        >>> result = execute(["echo", "hello"])
        >>> result.stdout.strip()
        'hello'

        Execute within a hypothetical environment:

        >>> # Assuming `my_env` is an object implementing EnvironmentProtocol
        >>> execute(["python", "--version"], environment=my_env)
    """
    from shlex import join as shlex_join  # noqa: PLC0415
    from subprocess import run as subprocess_run  # noqa: PLC0415

    if environment is not None:
        args = environment.get_args(args)

    kwargs.setdefault("text", True)
    kwargs.setdefault("check", True)
    kwargs.setdefault("start_new_session", True)

    logger.info("Running command: %s", shlex_join(args))
    logger.debug("Additional kwargs for subprocess.run: %s", kwargs)
    return subprocess_run(args, **kwargs)  # noqa: PLW1510, S603
