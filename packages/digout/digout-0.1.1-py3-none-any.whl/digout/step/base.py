"""Defines the abstract base class and common logic for all workflow steps."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generic

from pydantic import BaseModel, ConfigDict, Field

from .._utils.path import ResolvedPath  # noqa: TC001 (needed by Pydantic)
from .._utils.std import StdConfig
from ..config.step import StepConfig
from ..core.step import StepKey, StepKind, T_co
from ..core.stream import StreamProtocol
from ..stream.base import WithChunkTypeProtocol

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ..context import Context

__all__ = ["StepBase", "UnresolvedStdConfig", "resolve_placeholders"]

logger = getLogger(__name__)


def resolve_placeholders(
    string: str, /, placeholders: Mapping[str, Any], *, warn_missing: bool = False
) -> str:
    """Replace placeholder keys in a string with their values.

    This function uses Python's ``str.format(**placeholders)`` to perform the
    replacement.

    Args:
        string: The string containing placeholders (e.g., ``/path/{name}``).
        placeholders: A dictionary mapping placeholder names to their values.
        warn_missing: If ``True``, logs a warning if the string did not contain
            any placeholders to replace.

    Returns:
        The string with placeholders resolved.
    """
    resolved_string = string.format(**placeholders)
    if warn_missing and string == resolved_string:
        logger.warning(
            "String '%s' does not contain any placeholders to resolve.", string
        )
    return resolved_string


class UnresolvedStdConfig(BaseModel):
    """A data model for standard I/O log paths that may contain placeholders."""

    stdout: ResolvedPath | None = None
    """Path to the standard output log file."""

    stderr: ResolvedPath | None = None
    """Path to the standard error log file."""

    def resolve(
        self, placeholders: Mapping[str, Any], *, warn_missing: bool = False
    ) -> StdConfig:
        """Apply placeholders to the stdout and stderr paths.

        Args:
            placeholders: A mapping of placeholder names to their values.
            warn_missing: If ``True``, warns if paths do not contain placeholders.

        Returns:
            A ``StdConfig`` instance with fully resolved, absolute paths.
        """
        resolved_stdout = (
            Path(
                resolve_placeholders(
                    stdout.as_posix(), placeholders, warn_missing=warn_missing
                )
            )
            .expanduser()
            .resolve()
            if (stdout := self.stdout)
            else None
        )
        resolved_stderr = (
            Path(
                resolve_placeholders(
                    stderr.as_posix(), placeholders, warn_missing=warn_missing
                )
            )
            .expanduser()
            .resolve()
            if (stderr := self.stderr)
            else None
        )
        return StdConfig(stdout=resolved_stdout, stderr=resolved_stderr)


class StepBase(BaseModel, ABC, Generic[T_co]):
    """An abstract base class that provides the common structure for workflow steps.

    This class implements the :py:class:`~digout.core.step.StepProtocol` protocol,
    and handles boilerplate logic such as input validation,
    configuration saving, I/O redirection, and completion checking via a
    :py:attr:`StepBase.done_path` file.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    log: UnresolvedStdConfig = Field(default_factory=UnresolvedStdConfig)
    """Configuration for redirecting stdout/stderr, may contain placeholders."""

    step_path: ResolvedPath | None = None
    """Path for saving a snapshot of the step's configuration for reproducibility.

    If set, the configuration is saved before execution in :py:meth:`run`.
    May contain placeholders like ``{name}`` or ``{idx}``.
    """

    done_path: ResolvedPath | None = None
    """Path to a marker file created upon successful completion of the step.

    This file is the primary mechanism for checking if a step has already run.
    May contain placeholders like ``{name}`` or ``{idx}``.
    """

    # Private methods ================================================================
    def _validate_sources(self, sources: Mapping[str, object], /) -> None:
        """Ensure the provided source keys match the step's declared dependencies.

        Dependencies are declared via the :py:meth:`get_source_keys` method.
        """
        expected_source_keys = self.get_source_keys()
        source_keys = set(sources.keys())
        if expected_source_keys != source_keys:
            msg = (
                f"Expected sources: {', '.join(map(repr, expected_source_keys))}. "
                f"Got: {', '.join(map(repr, source_keys))}. "
                "Please ensure the sources match the expected keys."
            )
            raise ValueError(msg)

    def _log(self) -> None:
        """Log the step's configuration details."""
        logger.debug("Step configuration: %s", self.model_dump(mode="json"))
        logger.debug("Sources: %s", self.get_source_keys())

    def _get_step_config(
        self, sources: Mapping[StepKey, object], context: Context, /
    ) -> StepConfig:
        """Create a serializable configuration object for this step."""
        return StepConfig(
            step_key=self.get_key(), step=self, sources=dict(sources), context=context
        )

    @abstractmethod
    def _run(self, sources: Mapping[StepKey, object], context: Context, /) -> T_co:
        """Define the unique execution logic for the step.

        Args:
            sources: A mapping from dependency keys to their outputs.
            context: The current workflow execution context.

        Returns:
            The output (target) of this step's execution.
        """

    def _has_run(self, _: Context, /) -> bool:
        """Define custom logic for checking if a step is already complete.

        This method is only called if :py:attr:`done_path`` is not set. It can be used
        to check for the existence of output files or other completion criteria.

        Args:
            context: The current workflow execution context.

        Returns:
            ``True`` if the step is considered complete, otherwise ``False``.
        """
        return False

    @abstractmethod
    def get_target(self, context: Context, /) -> T_co:
        """Retrieve the step's output without running the step itself.

        This is used to get a reference to an expected output object, which might
        already exist.

        Args:
            context: The current workflow execution context.

        Returns:
            The output (target) object of this step.

        Raises:
            NotRunError: If the target cannot be determined without first
                running the step.
        """

    # Implementation of StepProtocol methods =========================================
    # Default implementation, could be overridden by subclasses ----------------------
    @classmethod
    def get_key(cls) -> str:
        """Return the unique identifier for the step (defaults to the class name)."""
        return cls.__name__

    @property
    def kind(self) -> StepKind:
        """:py:attr:`~digout.core.step.StepKind.CHUNK`."""
        # Override this method to use another step kind.
        return StepKind.CHUNK

    @classmethod
    def get_stream_type(cls) -> Any:
        """Raise ``NotImplementedError``."""
        # Override this method to return the type of stream produced by this step.
        msg = (
            f"{cls.__name__}.get_stream_type() is not implemented. "
            "This could mean that a stream was never defined for this step."
        )
        raise NotImplementedError(msg)

    @classmethod
    def get_chunk_type(cls) -> Any:
        """Return the type of chunk produced by this step.

        If the stream of the step is provided through :py:meth:`get_stream_type`,
        the method tries to infer the chunk type from it, through
        the :py:meth:`~digout.stream.base.WithChunkTypeProtocol.get_chunk_type` method
        if the stream class implements the
        :py:class:`~digout.stream.base.WithChunkTypeProtocol` protocol.

        Otherwise, it raises a ``NotImplementedError``.

        Raises:
            NotImplementedError: If the step does not implement a stream type
                or if the stream type does not implement the
                :py:class:`~digout.stream.base.WithChunkTypeProtocol` protocol.
        """
        stream_cls = cls.get_stream_type()
        if isinstance(stream_cls, StreamProtocol) and isinstance(
            stream_cls, WithChunkTypeProtocol
        ):
            return stream_cls.get_chunk_type()

        msg = f"{cls.__name__}.get_chunk_type() is not implemented."
        raise NotImplementedError(msg)

    def get_source_keys(self) -> set[str]:
        """Return an empty set."""
        # Override this method to return the set of source keys this step depends on.
        return set()

    # Not meant to be overridden by subclasses ---------------------------------------
    def run(self, sources: Mapping[StepKey, object], context: Context, /) -> T_co:
        """Run the step.

        This final method handles validation, logging, configuration saving,
        I/O redirection, calling the custom ``_run`` logic, and creating the
        completion marker file. It should not be overridden by subclasses.

        Args:
            sources: A mapping from dependency keys to their outputs.
            context: The context in which the step is executed.

        Returns:
            The output (target) produced by the ``_run`` method.
        """
        # Warn for missing placeholders only for chunk steps
        # since it's alright for stream steps not to have placeholders
        warn_no_placeholders = self.kind is StepKind.CHUNK
        self._validate_sources(sources)
        self._log()

        placeholders = context.placeholders

        if (step_path := self.step_path) is not None:
            step_path = (
                Path(
                    resolve_placeholders(
                        step_path.as_posix(),
                        placeholders,
                        warn_missing=warn_no_placeholders,
                    )
                )
                .expanduser()
                .resolve()
            )
            self._get_step_config(sources, context).to_yaml(step_path)

        resolved_std = self.log.resolve(
            placeholders=placeholders, warn_missing=warn_no_placeholders
        )
        with resolved_std.redirect_std():
            target = self._run(sources, context)

        if (done_path := self.done_path) is not None:
            done_path = (
                Path(
                    resolve_placeholders(
                        done_path.as_posix(),
                        placeholders,
                        warn_missing=warn_no_placeholders,
                    )
                )
                .expanduser()
                .resolve()
            )
            done_path.touch(exist_ok=True)
            logger.debug("Done file created at %s", done_path.as_posix())

        logger.info("Step '%s' completed successfully.", self.get_key())
        return target

    def has_run(self, context: Context, /) -> bool:
        """Check if the step is complete, prioritizing the :py:attr:`done_path`.

        If :py:attr:`done_path` is configured, this method checks for its existence.
        If it is not configured, it falls back to the custom ``_has_run`` logic.
        This method should not be overridden by subclasses.
        """
        if (done_path := self.done_path) is not None:
            done_path = Path(
                resolve_placeholders(
                    done_path.as_posix(),
                    context.placeholders,
                    warn_missing=self.kind is StepKind.CHUNK,
                )
            )
            return done_path.exists()
        return self._has_run(context)
