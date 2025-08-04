"""Provide a base class for steps that execute a Moore algorithm."""

from __future__ import annotations

import sys
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass, field
from importlib.abc import Traversable
from importlib.resources import as_file, files
from logging import getLogger
from pathlib import Path
from subprocess import DEVNULL
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, Any

from pydantic import ConfigDict, Field

from .._utils.envvar import get_updated_environ
from .._utils.ioyaml import dump_yaml
from .._utils.path import ResolvedPath, copy_file
from ..core.step import StepKey, T_co
from ..environment import Environment, execute
from ..stream.moore import MooreChunk
from .base import StepBase, resolve_placeholders

if TYPE_CHECKING:
    from collections.abc import Generator, Mapping
    from subprocess import CompletedProcess

    from ..context import Context

logger = getLogger(__name__)


MOORE_DIR = files("digout._moore")
"""A reference to the package directory containing shared Moore option files."""


@contextmanager
def _prepare_transversable_paths(
    resources: list[Path | Traversable],
) -> Generator[list[Path], None, None]:
    """Get concrete file paths from package resources.

    Some resources might be inside a zip file and need to be temporarily
    extracted to be used as a file. This manager handles that.

    Args:
        resources: A list of ``Path`` or ``importlib.abc.Traversable`` objects.

    Yields:
        A list of concrete, resolved ``Path`` objects.
    """
    with ExitStack() as stack:
        paths: list[Path] = []
        for resource in resources:
            if isinstance(resource, Path):
                paths.append(resource.resolve())
            elif isinstance(resource, Traversable):
                path = stack.enter_context(as_file(resource))
                logger.debug(
                    "Using resource '%s' as file: %s", resource, path.as_posix()
                )
                paths.append(path)
        yield paths


def _check_moore_files(moore_files: list[Path]) -> None:
    """Ensure that all provided file paths exist.

    Raises:
        ValueError: If the list of files is empty.
        FileNotFoundError: If any file in the list does not exist.
    """
    if not moore_files:
        msg = "No Moore files provided for the step."
        raise ValueError(msg)

    for moore_file in moore_files:
        if not moore_file.exists():
            msg = f"Moore file '{moore_file}' does not exist."
            raise FileNotFoundError(msg)


@dataclass(frozen=False)
class MooreConfig:
    """A data container for configuring a single Moore execution."""

    option_files: list[Path | Traversable]
    """A list of Gaudi option files (.py) to pass to ``gaudirun.py``."""

    temp_dir: Path
    """A temporary directory for storing intermediate configuration files."""

    environment_variables: dict[str, str] = field(default_factory=dict[str, str])
    """Environment variables to set for the ``gaudirun.py`` process."""


class MooreStepBase(StepBase[T_co]):
    """An abstract base class for steps that run a Moore algorithm.

    This class provides the boilerplate for executing ``gaudirun.py``. It handles
    the setup of temporary directories, and creating
    the necessary configuration files and environment variables.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    environment: Environment | None = None
    """The environment in which to execute ``gaudirun.py``."""

    executable: ResolvedPath | None = None
    """Path to the Moore executable.

    If ``None``, it is assumed to be in the ``PATH``.
    """

    moore_options: dict[str, Any] = Field(default_factory=dict)
    """A dictionary of Moore options specific to this step.

    These options will override any general options provided
    by the :py:attr:`~digout.stream.moore.MooreChunk.moore_options`
    attribute of the :py:class:`~digout.stream.moore.MooreChunk` instance
    passed as source to this step.
    """

    moore_options_path: ResolvedPath | None = None
    """Path for saving the final Moore options YAML file.

    This path can contain placeholders. If not set, a temporary file is used.
    """

    # Private methods ================================================================
    def __get_moore_options_paths(
        self, placeholders: Mapping[str, str], temp_dir: Path
    ) -> Path:
        """Resolve the path for the Moore options YAML file."""
        moore_options_path = self.moore_options_path
        if moore_options_path is None:
            return temp_dir / "moore_options.yaml"

        return (
            Path(resolve_placeholders(moore_options_path.as_posix(), placeholders))
            .expanduser()
            .resolve()
        )

    def __get_moore_options(self, source: MooreChunk, /) -> dict[str, Any]:
        """Merge Moore options from the source chunk and this step."""
        moore_options = source.moore_options.copy()

        if "input_files" in moore_options:
            msg = (
                "The 'input_files' option should be set "
                "through the 'input_paths' attribute."
            )
            raise ValueError(msg)

        moore_options["input_files"] = source.paths
        moore_options.update(self.moore_options)

        return moore_options

    def _parse_sources(
        self, sources: Mapping[StepKey, object], /
    ) -> tuple[MooreChunk, Path | None]:
        """Extract the Moore chunk and optional XML catalog from the input sources."""
        moore_chunk = sources["create_moore_stream"]
        if not isinstance(moore_chunk, MooreChunk):
            msg = (
                f"Expected 'create_moore_stream' to be a MooreChunk, "
                f"but got {type(moore_chunk).__name__}."
            )
            raise TypeError(msg)

        xml_catalog_path = sources.get("generate_xml_catalog")
        if xml_catalog_path is not None and not isinstance(xml_catalog_path, Path):
            msg = (
                f"Expected 'generate_xml_catalog' to be a Path or None, "
                f"but got {type(xml_catalog_path).__name__}."
            )
            raise TypeError(msg)
        return moore_chunk, xml_catalog_path

    # Methods to be implemented by subclasses ========================================
    @contextmanager
    def _prepare_moore_config(
        self,
        moore_chunk: MooreChunk,
        xml_catalog_path: Path | None,
        placeholders: Mapping[str, str],
    ) -> Generator[MooreConfig, None, None]:
        """Prepare the base configuration for running Moore.

        This context manager creates a temporary directory, prepares the common
        option files and environment variables, and yields a :py:class:`MooreConfig`
        object that can be further modified by subclasses before execution.

        Defaults configuration includes:

        - :py:attr:`~MooreConfig.temp_dir` set to a temporary directory
        - :py:attr:`~MooreConfig.option_files` containing ``options.py``
          and optionally ``catalog.py`` if `xml_catalog_path` is provided.
        - :py:attr:`~MooreConfig.environment_variables` containing
          `DIGOUT_MOORE_OPTIONS_YAML` pointing to the YAML file with Moore options
          and optionally `DIGOUT_MOORE_XML_CATALOG` if `xml_catalog_path` is provided.

        Yields:
            A :py:class:`MooreConfig` object with the base configuration.
        """
        with TemporaryDirectory() as tmpdir:
            temp_dir = Path(tmpdir).resolve()
            moore_options_path = self.__get_moore_options_paths(placeholders, temp_dir)

            option_files = [
                # Read `DIGOUT_MOORE_OPTIONS_YAML` and set the `Moore.options`.
                MOORE_DIR / "options.py"
            ]
            environment_variables = {
                "DIGOUT_MOORE_OPTIONS_YAML": moore_options_path.as_posix(),
            }

            if xml_catalog_path is not None:
                # `catalog.py` reads `DIGOUT_MOORE_XML_CATALOG`
                # and sets the XML catalog for the Moore input.
                option_files.append(MOORE_DIR / "catalog.py")
                # copy xml_catalog_path to a temporary file in case it gets modified

                temporary_xml_catalog_path = temp_dir / "catalog.xml"
                copy_file(xml_catalog_path, temporary_xml_catalog_path)

                environment_variables["DIGOUT_MOORE_XML_CATALOG"] = (
                    temporary_xml_catalog_path.as_posix()
                )

            dump_yaml(self.__get_moore_options(moore_chunk), moore_options_path)

            yield MooreConfig(
                option_files=option_files,
                temp_dir=temp_dir,
                environment_variables=environment_variables,
            )

    # Implementation of StepBase =====================================================
    def _run_moore(
        self, option_files: list[Path], new_environment_variables: dict[str, str]
    ) -> CompletedProcess[str]:
        """Construct and execute the `gaudirun.py` command."""
        args: list[str] = []
        if (executable := self.executable) is not None:
            args.append(executable.as_posix())
        args.append("gaudirun.py")

        environment_variables: dict[str, str] | None
        if new_environment_variables:
            logger.debug(
                "Adding environment variables for step '%s': %s",
                self.get_key(),
                new_environment_variables,
            )
            environment_variables = get_updated_environ(**new_environment_variables)
        else:
            logger.debug(
                "No additional environment variables for step '%s'.",
                self.get_key(),
            )
            environment_variables = None

        # Add moore files to the arguments
        _check_moore_files(option_files)
        args.extend([option_file.as_posix() for option_file in option_files])

        return execute(
            args=args,
            environment=self.environment,
            env=environment_variables,
            # to avoid prompting for PEM passphrase
            stdin=DEVNULL,
            # Redirect stdout and stderr to the proper streams
            # since they might be redirected in the `run` method
            stdout=sys.stdout,
            stderr=sys.stderr,
        )

    def _run(self, sources: Mapping[StepKey, object], context: Context, /) -> T_co:
        """Prepare and run the Moore algorithm."""
        moore_chunk, xml_catalog_path = self._parse_sources(sources)
        with self._prepare_moore_config(
            moore_chunk, xml_catalog_path, context.placeholders
        ) as moore_config:
            transversable_paths = moore_config.option_files
            if not transversable_paths:
                msg = (
                    "No Moore option files provided for the step. "
                    "At least one option file is required to run the Moore algorithm."
                )
                raise ValueError(msg)

            with _prepare_transversable_paths(transversable_paths) as option_files:
                self._run_moore(
                    option_files=option_files,
                    new_environment_variables=moore_config.environment_variables,
                )

        return self.get_target(context)

    # Implementation of StepBase =====================================================
    def get_source_keys(self) -> set[str]:
        """Return the set of step keys this step depends on.

        :py:class:`"create_moore_stream" <digout.step.createmoorestream.CreateMooreStreamStep>`
        and
        :py:class:`"generate_xml_catalog" <digout.step.generatexmlcatalog.GenerateXMLCatalogStep>`
        """  # noqa: E501
        return {"create_moore_stream", "generate_xml_catalog"}
