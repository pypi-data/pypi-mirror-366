"""Defines the :py:class:`MooreStream` and :py:class:`MooreChunk` models.

These models represent the data inputs for Moore-based steps.
A :py:class:`MooreStream` is typically created by
:py:class:`~digout.step.createmoorestream.CreateMooreStreamStep` step,
and is consumed by steps that inherits from
:py:class:`~digout.step._moore.MooreStepBase`, such as
:py:class:`~digout.step.digi2root.DIGI2ROOTStep`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field

from .._utils.resources import get_tmpdir
from ..context import Context

__all__ = ["MooreChunk", "MooreStream"]


class MooreChunk(BaseModel):
    """Represents a single group of files to be processed by a Moore step."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    paths: list[str]
    """A list of file paths for this chunk, which can be LFNs or PFNs.

    Logical File Names (LFNs) must be prefixed with ``LFN:``. Physical File
    Names (PFNs) should be regular file system paths.
    """

    moore_options: dict[str, Any] = Field(default_factory=dict)
    """A dictionary of Moore options specific to this chunk."""

    @property
    def lfns(self) -> list[str]:
        """Returns a new list containing only the LFNs from the :py:attr:`paths`."""
        return [path for path in self.paths if path.startswith("LFN:")]


class MooreStream(BaseModel):
    """A stream of data files that can be divided into chunks for Moore steps.

    This class conforms to the :py:class:`~digout.core.stream.StreamProtocol`
    interface. It manages a list of input file paths and divides them into
    :py:class:`MooreChunk` objects (see :py:meth:`get_chunk`). It also provides
    context to downstream chunk steps (see :py:meth:`get_chunk_context`).
    """

    paths: list[str]
    """A list of all file paths in the stream (LFNs or PFNs).

    LFNs must be prefixed with ``LFN:``.
    """

    moore_options: dict[str, Any] = Field(default_factory=dict)
    """A dictionary of Moore options that apply to all chunks in the stream."""

    n_files_per_chunk: Annotated[int, Field(ge=1)] | None = 1
    """The number of files to group into each :py:class:`MooreChunk`.

    If ``None``, all files are placed into a single chunk.
    """

    # Private methods ================================================================
    def _get_chunk_paths(self, index: int) -> list[str]:
        """Return the list of file paths for the chunk at the given index."""
        n_files_per_chunk = self.n_files_per_chunk
        paths = self.paths

        if n_files_per_chunk is None:
            return paths

        start = index * n_files_per_chunk
        end = start + n_files_per_chunk
        return paths[start:end]

    # Implementation of StreamProtocol ===============================================
    @property
    def n_chunks(self) -> int:
        """The total number of chunks this stream is divided into.

        Raises:
            ValueError: If :py:attr:`paths` is empty.
        """
        paths = self.paths

        if not paths:
            msg = "No paths provided in the stream."
            raise ValueError(msg)

        if self.n_files_per_chunk is None:
            return 1
        return (len(paths) + self.n_files_per_chunk - 1) // self.n_files_per_chunk

    def get_chunk(self, index: int, /) -> MooreChunk:
        """Create and return the :py:class:`MooreChunk` for the given index."""
        chunk_paths = self._get_chunk_paths(index)
        return MooreChunk(paths=chunk_paths, moore_options=self.moore_options)

    def get_chunk_context(self, index: int, context: Context) -> Context:
        """Generate a :py:class:`~digout.context.Context` with placeholders specific to the given chunk.

        The enriched context includes the following placeholders:

        - ``idx``: The numerical index of the chunk.
        - ``name``: A string name derived from the file names in the chunk.
        - ``tmpdir``: A unique temporary directory path for the chunk.
        """  # noqa: E501
        chunk_paths = self._get_chunk_paths(index)
        assert chunk_paths, "Chunk paths cannot be empty."
        chunk_name = "-".join(Path(chunk_path).stem for chunk_path in chunk_paths)
        return context.combine(
            Context(
                placeholders={
                    "name": chunk_name,
                    "idx": str(index),
                    # a temporary directory for each chunk
                    "tmpdir": get_tmpdir().as_posix(),
                }
            )
        )

    # Implementation of WithChunkCls ================================================
    @classmethod
    def get_chunk_type(cls) -> type[MooreChunk]:
        """Return the type of chunk this stream produces, :py:class:`MooreChunk`.

        By implementing this, this class conforms to the
        :py:class:`~digout.stream.base.WithChunkTypeProtocol` interface.
        """
        return MooreChunk

    # Public methods ================================================================
    @property
    def lfns(self) -> list[str]:
        """Return a new list containing only the LFNs from the :py:attr:`paths`."""
        return [path for path in self.paths if path.startswith("LFN:")]
