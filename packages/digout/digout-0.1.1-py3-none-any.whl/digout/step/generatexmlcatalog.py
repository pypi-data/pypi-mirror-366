"""Defines a step to generate an XML file catalog from Logical File Names (LFNs)."""

from __future__ import annotations

import sys
from logging import getLogger
from pathlib import Path
from shutil import move
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING

from pydantic import Field

from .._utils.path import ResolvedPath, create_directory
from ..core.step import NotRunError, StepKey, StepKind
from ..environment import DiracEnvironment, Environment, execute
from ..stream.moore import MooreChunk, MooreStream
from .base import StepBase

if TYPE_CHECKING:
    from collections.abc import Mapping
    from types import UnionType

    from ..context import Context

logger = getLogger(__name__)


__all__ = ["GenerateXMLCatalogStep"]


class GenerateXMLCatalogStep(StepBase[Path | None]):
    """Generates an XML catalog from Logical File Names (LFNs) in a Moore stream/chunk.

    This step wraps the ``dirac-bookkeeping-genXMLCatalog`` command-line tool,
    which resolves Logical File Names (LFNs) into Physical File Names (PFNs)
    and stores the mapping in an XML file. The step can be configured to operate
    on an entire stream of LFNs or on a smaller chunk.
    """

    output: ResolvedPath
    """The path where the output XML catalog file will be saved.

    This path can contain placeholders like ``{name}`` or ``{idx}``, which
    will be resolved at runtime.
    """

    environment: Environment | None = Field(default_factory=DiracEnvironment)
    """The environment used to execute the DIRAC command."""

    on_chunk: bool = True
    """Whether this step is a :py:attr:`~core.step.StepKind.CHUNK` step.

    If ``True``, the step operates on a single chunk of LFNs.
    If ``False``, it operates on the entire stream of LFNs at once.
    """

    # Private methods ================================================================
    def _get_output_path(self, placeholders: Mapping[str, str], /) -> Path:
        """Resolve the output path string using the given placeholders."""
        return (
            Path(self.output.as_posix().format(**placeholders)).expanduser().resolve()
        )

    def _generate_xml_catalog_path(
        self, lfns: list[str], xml_catalog_path: Path
    ) -> None:
        """Execute the DIRAC command to generate the XML catalog.

        The command is run in a temporary directory because it creates an extra
        ``.py`` file alongside the XML catalog, which can then be discarded.

        Args:
            lfns: A list of LFNs to include in the catalog.
            xml_catalog_path: The final destination path for the generated XML file.
        """
        with TemporaryDirectory() as temp_dir:
            temporary_path = Path(temp_dir) / "catalog.xml"
            execute(
                [
                    "dirac-bookkeeping-genXMLCatalog",
                    "--Ignore",  # Ignore missing files
                    "--LFNs",
                    ",".join(lfns),  # comma-separated list of LFNs
                    "--Catalog=" + temporary_path.as_posix(),
                ],
                environment=self.environment,
                # Redirect stdout and stderr to the proper streams
                # since they might be redirected in the `run` method
                stdout=sys.stdout,
                stderr=sys.stderr,
            )

            # Delete the .py file created by the command
            py_file = temporary_path.with_suffix(".py")
            if py_file.exists():
                logger.debug("Deleting Python file: %s", py_file)
                py_file.unlink()

            # Move the generated XML catalog to the output path
            create_directory(xml_catalog_path.parent)
            logger.debug("Moving XML catalog to output path: %s", xml_catalog_path)
            # Use shutil.move to allow moving file across filesystems
            move(temporary_path, xml_catalog_path)

    # Implementation of StepBase =====================================================
    def _parse_sources(self, sources: Mapping[str, object], /) -> list[str]:
        """Extract the LFN source from the step's inputs."""
        source = sources["create_moore_stream"]
        assert isinstance(source, (MooreChunk, MooreStream)), (
            f"Expected source to be a MooreChunk or MooreStream, got {type(source)}"
        )
        return source.lfns

    def _run(
        self, sources: Mapping[StepKey, object], context: Context, /
    ) -> Path | None:
        """Execute the logic to generate the XML catalog.

        If the input source contains no LFNs, the step does nothing and returns
        ``None``, as no catalog is needed.
        """
        lfns = self._parse_sources(sources)
        if not lfns:
            return None

        output_path = self._get_output_path(context.placeholders)
        self._generate_xml_catalog_path(lfns, output_path)
        return output_path

    def _has_run(self, context: Context, /) -> bool:
        """Check for completion by seeing if the output file exists."""
        return self._get_output_path(context.placeholders).exists()

    def get_target(self, context: Context, /) -> Path | None:
        """Return the path to the generated XML catalog, or ``None``.

        Raises:
            NotRunError: If the target does not exist. The file might not exist
                because the step has not run, or because it was skipped due to
                having no input LFNs.
                Running the step is required to distinguish between these two cases.
        """
        output_path = self._get_output_path(context.placeholders)
        if output_path.exists():
            return output_path
        msg = (
            f"The step {self.get_key()} needs to be run first to return its target. "
            "The reason is that if the source has no LFNs, the XML catalog "
            "does not need to be generated."
        )
        raise NotRunError(msg)

    @classmethod
    def get_key(cls) -> str:
        """Return the key for this step, ``generate_xml_catalog``."""
        return "generate_xml_catalog"

    def get_source_keys(self) -> set[str]:
        """Return the set of step keys this step depends on.

        :py:class:`"create_moore_stream" <digout.step.createmoorestream.CreateMooreStreamStep>`
        and
        :py:class:`"generate_grid_proxy" <digout.step.generategridproxy.GenerateGridProxyStep>`
        """  # noqa: E501
        return {"generate_grid_proxy", "create_moore_stream"}

    @property
    def kind(self) -> StepKind:
        """:py:attr:`~digout.core.step.StepKind.CHUNK`
        if :py:attr:`~digout.step.generatexmlcatalog.GenerateXMLCatalogStep.on_chunk`
        is ``True``, :py:attr:`~digout.core.step.StepKind.STREAM` otherwise.
        """  # noqa: D205
        return StepKind.CHUNK if self.on_chunk else StepKind.STREAM

    @classmethod
    def get_stream_type(cls) -> UnionType:
        """Return ``Path | None`` as the stream type for this step."""
        return Path | None

    @classmethod
    def get_chunk_type(cls) -> UnionType:
        """Return ``Path | None`` as the chunk type for this step."""
        return Path | None
