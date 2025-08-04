"""The logging configuration for running a step."""

from __future__ import annotations

from contextlib import contextmanager, nullcontext, redirect_stderr, redirect_stdout
from logging import Handler, StreamHandler, getLogger
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

from .path import PathLike, ResolvedPath, create_directory

if TYPE_CHECKING:
    from collections.abc import Generator
    from io import TextIOWrapper

logger = getLogger(__name__)

__all__ = ["StdConfig"]


def _prepare_path(path: PathLike) -> Path:
    """Prepare a path."""
    path = Path(path)
    create_directory(path.parent)
    return path


def _get_file_context(
    spec: PathLike | None,
) -> TextIOWrapper[Any] | nullcontext[None]:
    """Get a context manager for file redirection."""
    if spec is None:
        return nullcontext()
    return _prepare_path(spec).open("w")


def _propagate_handler_properties(new: Handler, old: Handler) -> None:
    """Propagate properties from one logging handler to another."""
    new.setLevel(old.level)
    new.setFormatter(old.formatter)
    for handler_filter in old.filters:
        new.addFilter(handler_filter)


@contextmanager
def _redirect_logging(file: TextIOWrapper[Any]) -> Generator[None, None, None]:
    logger = getLogger()

    previous_handlers = logger.handlers[:]
    if previous_handlers:
        logger.debug("Redirecting logging to %s", file.name)
        handler = StreamHandler(file)
        _propagate_handler_properties(handler, previous_handlers[0])
        logger.handlers = [handler]
        try:
            yield
        finally:
            logger.handlers = previous_handlers
            handler.close()


class StdConfig(BaseModel):
    """Configuration for standard output and error redirection."""

    stdout: ResolvedPath | None = None
    """Path to redirect standard output.

    If a Path is provided, standard output will be redirected to that path.
    If ``None``, standard output will not be redirected.
    """

    stderr: ResolvedPath | None = None
    """Path to redirect standard error.

    If a Path is provided, standard error will be redirected to that path.
    If ``None``, standard error will not be redirected.
    """

    def _log(self) -> None:
        """Log the configuration of standard output and error paths."""
        if self.stdout:
            logger.info("Redirecting stdout to %s", self.stdout)
        if self.stderr:
            logger.info("Redirecting stderr to %s", self.stderr)

    @contextmanager
    def get_std(
        self,
    ) -> Generator[
        tuple[TextIOWrapper[Any] | None, TextIOWrapper[Any] | None], None, None
    ]:
        """Get a context manager for standard output and standard error redirection."""
        with (
            _get_file_context(self.stdout) as stdout,
            _get_file_context(self.stderr) as stderr,
        ):
            yield stdout, stderr

    @contextmanager
    def redirect_std(self) -> Generator[None, None, None]:
        """Redirect standard output and standard error to the specified paths."""
        self._log()
        with (
            self.get_std() as (stdout, stderr),
            redirect_stdout(stdout) if stdout is not None else nullcontext(),
            redirect_stderr(stderr) if stderr is not None else nullcontext(),
            _redirect_logging(stderr) if stderr is not None else nullcontext(),
        ):
            yield
