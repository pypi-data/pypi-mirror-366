"""Define a step to create a ``MooreStream`` from a bookkeeping path."""

from __future__ import annotations

import sys
from logging import getLogger
from typing import TYPE_CHECKING, Annotated

from pydantic import Field

from .._utils.ioyaml import load_yaml
from .._utils.path import ResolvedPath, get_src_path
from ..bookkeeping._info import BKInfo
from ..context import Context
from ..core.step import NotRunError, StepKey, StepKind
from ..environment import Environment, execute
from ..stream.moore import MooreStream
from .base import StepBase
from .selector import Selector  # noqa: TC001 (needed by Pydantic)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ..context import Context

logger = getLogger(__name__)

__all__ = ["CreateMooreStreamStep"]


class CreateMooreStreamStep(StepBase[MooreStream]):
    """Creates a :py:class:`~digout.stream.moore.MooreStream` from a DIRAC bookkeeping path.

    This step runs an external script to query a given bookkeeping path,
    resolving it into a list of Logical File Names (LFNs) and associated Moore
    options.

    It saves this information to an intermediate YAML file and then
    constructs a :py:class:`~digout.stream.moore.MooreStream` object from it.
    """  # noqa: E501

    input: str
    """The DIRAC bookkeeping path to query for data files."""

    output: ResolvedPath
    """Path where the bookkeeping information (as a YAML file) will be saved."""

    environment: Environment | None = None
    """The environment in which to run the bookkeeping query script."""

    select: Selector | None = None
    """An optional selector to filter the list of files retrieved from bookkeeping."""

    n_files_per_chunk: Annotated[int, Field(ge=1)] | None = 1
    """The number of files to group into each chunk in the final :py:class:`~digout.stream.moore.MooreStream`.

    If ``None``, all files are placed into a single chunk.
    """  # noqa: E501

    # Private methods ================================================================
    def _execute(self) -> None:
        """Run the external script to produce the bookkeeping info YAML file."""
        python_executable = (
            [sys.executable]
            if self.environment is None
            # use the Python interpreter from the environment
            else ["/usr/bin/env", "python3"]
        )
        execute(
            [
                *python_executable,
                "-m",
                "digout.script._produce_bookkeeping_info",
                self.input,
                self.output.as_posix(),
            ],
            environment=self.environment,
            # Redirect stdout and stderr to the proper streams
            # since they might be redirected in the `run` method
            stdout=sys.stdout,
            stderr=sys.stderr,
            # Run in the source directory
            # to ensure the script can find `digout` package
            # without installing it
            cwd=get_src_path(),
        )

    # Implementation of StepBase =====================================================
    def _has_run(self, _: Context, /) -> bool:
        """Check if the step is complete by looking for the output YAML file."""
        return self.output.exists()

    def _run(self, _: Mapping[StepKey, object], context: Context, /) -> MooreStream:
        """Run the bookkeeping query script and returns the resulting stream."""
        self._execute()
        return self.get_target(context)

    @classmethod
    def get_key(cls) -> str:
        """Return the key for this step, ``create_moore_stream``."""
        return "create_moore_stream"

    def get_source_keys(self) -> set[str]:
        """Return the set of step keys this step depends on.

        :py:class:`"generate_grid_proxy" <digout.step.generategridproxy.GenerateGridProxyStep>`
        """  # noqa: E501
        return {"generate_grid_proxy"}

    @property
    def kind(self) -> StepKind:
        """:py:attr:`~digout.core.step.StepKind.STREAM`."""
        return StepKind.STREAM

    @classmethod
    def get_stream_type(cls) -> type[MooreStream]:
        """Return the type of stream produced by this step.

        This is :py:class:`~digout.stream.moore.MooreStream`.
        """
        return MooreStream

    def get_target(self, context: Context, /) -> MooreStream:  # noqa: ARG002
        """Load the generated YAML file and constructs the ``MooreStream`` object.

        This method reads the :py:attr:`output` YAML file,
        applies the optional :py:attr:`select` selector, and returns a fully
        configured :py:class:`~digout.stream.moore.MooreStream` instance.

        Args:
            context: The current workflow execution context.

        Returns:
            The final :py:class:`~digout.stream.moore.MooreStream` object.

        Raises:
            NotRunError: If the intermediate :py:attr:`output` file does not exist.
        """
        output_path = self.output
        if not output_path.exists():
            msg = (
                f"The step {self.get_key()} needs to be run first "
                "to produce the target stream."
            )
            raise NotRunError(msg)

        bk_info = BKInfo.model_validate(load_yaml(output_path))
        paths = ["LFN:" + lfn for lfn in bk_info.lfns]

        if (selector := self.select) is not None:
            logger.debug(
                "Applying selector %s to the %d paths in the stream.",
                selector,
                len(paths),
            )
            paths = selector.select(paths)
            logger.debug(
                "After applying the selector, the stream contains %d paths.",
                len(paths),
            )

        return MooreStream(
            paths=paths,
            moore_options=bk_info.get_moore_options(),
            n_files_per_chunk=self.n_files_per_chunk,
        )
