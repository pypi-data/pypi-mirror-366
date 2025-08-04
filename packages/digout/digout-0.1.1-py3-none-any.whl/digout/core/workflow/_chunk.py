"""Workflow composed of **chunk steps** whose *sources* are streams.

This object lives **after** the stream phase: each stream produced earlier is
kept as a source node, while only chunk steps remain in the graph.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from logging import getLogger
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from .._graph.base import n
from ..context import ContextProtocol
from ..step import StepKind
from ..stream import StreamProtocol, get_context_for_chunk, get_n_chunks
from ._base import WorkflowBase
from ._run import RunnableWorkflow

if TYPE_CHECKING:
    from ...step import StepKey

_unset = object()

C_stream = TypeVar("C_stream", bound=ContextProtocol)
C_chunk = TypeVar("C_chunk", bound=ContextProtocol)

logger = getLogger(__name__)


def _get_stream(
    key: StepKey, attrs: dict[str, object]
) -> StreamProtocol[Any, Any, Any]:
    """Return the stream stored in ``attrs["target"]`` for the step ``step_key``.

    Raises:
        KeyError: If no target stream is present.
    """
    if (stream := attrs.get("target", _unset)) is not _unset:
        assert isinstance(stream, StreamProtocol)
        return stream
    msg = f"Step key {key!r} does not have a target set in the attributes."
    raise KeyError(msg)


@dataclass(frozen=True)
class ChunkWorkflow(WorkflowBase[C_stream], Generic[C_stream, C_chunk]):
    """Workflow of chunk steps fed by stream sources.

    The stored :py:attr:`context` is still the *stream* context.

    To obtain a runnable workflow for one chunk call :py:meth:`select_chunk`.
    """

    # Private methods ================================================================
    def _get_context(self, chunk_idx: int, /) -> C_chunk:
        """Build the context for ``chunk_idx``."""
        return get_context_for_chunk(
            context=self.context, streams=self._streams, chunk_idx=chunk_idx
        )

    @cached_property
    def _stream_keys(self) -> set[StepKey]:
        """Keys of stream sources in the graph.

        Raises:
            RuntimeError: If no stream sources are present (should not happen).
        """
        stream_keys = {
            node
            for node, attrs in self.graph.nodes(data=True)
            if (
                (target := n(attrs).get("target", _unset)) is not None
                and isinstance(target, StreamProtocol)
            )
        }
        if not stream_keys:
            msg = (
                "The chunk workflow does not contain any stream keys. "
                "This is unexpected for a chunk workflow."
            )
            raise RuntimeError(msg)
        return stream_keys

    @cached_property
    def _streams(self) -> dict[StepKey, StreamProtocol[Any, C_stream, C_chunk]]:
        """Mapping from :py:attr:`_stream_keys` to their stream objects."""
        return {
            key: _get_stream(key, self.graph.nodes[key]) for key in self._stream_keys
        }

    # Public methods ===============================================================
    @property
    def n_chunks(self) -> int:
        """Common number of chunks across all streams.

        Raises:
            ValueError: If the streams disagree on their length.
        """
        return get_n_chunks(self._streams.values())

    def select_chunk(
        self, chunk_idx: int, /, *, reduce: bool = True
    ) -> RunnableWorkflow[C_chunk]:
        """Return a runnable workflow for ``chunk_idx``.

        Args:
            chunk_idx: Zero-based chunk index.
            reduce: If ``True`` (default) trim the graph to the minimal set of
                steps needed for the required targets.

        Returns:
            A runnable workflow with the selected chunks.

        Notes:
            Targets that are **not** streams are passed through unchanged; they
            are treated as per-chunk constants.
        """
        graph = self.graph.copy()

        for stream_key in self._stream_keys:
            target = _get_stream(stream_key, graph.nodes[stream_key])
            graph.nodes[stream_key]["target"] = target.get_chunk(chunk_idx)

        context = self._get_context(chunk_idx)
        workflow = RunnableWorkflow(graph=graph, context=context, kind=StepKind.CHUNK)
        if reduce:
            workflow = workflow.reduce()
        return workflow
