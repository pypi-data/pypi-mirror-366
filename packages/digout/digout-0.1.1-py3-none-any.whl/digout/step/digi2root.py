"""Defines a step that runs the DIGI-to-ROOT Moore algorithm."""

from __future__ import annotations

from contextlib import contextmanager
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING

from .._utils.ioyaml import dump_yaml
from .._utils.path import ResolvedPath  # noqa: TC001 (needed by Pydantic)
from ..stream.moore import MooreChunk
from ._moore import MOORE_DIR, MooreConfig, MooreStepBase
from .base import resolve_placeholders

if TYPE_CHECKING:
    from collections.abc import Generator, Mapping

    from ..context import Context
    from ..stream.moore import MooreChunk


logger = getLogger(__name__)

__all__ = ["DIGI2ROOTStep"]


class DIGI2ROOTStep(MooreStepBase[Path]):
    """Runs the PrTrackerDumper algorithm to dump hits and particles to ROOT files.

    This step processes raw detector data (DIGI) to produce ROOT files
    containing particle and hit information.
    It extends :py:class:`~digout.step._moore.MooreStepBase` to
    handle the specific configuration required by this algorithm.

    The corresponding algorithm is defined in the Allen framework,
    at `Dumpers/RootDumpers/PrTrackerDumper.cpp <https://gitlab.cern.ch/lhcb/Allen/-/blob/master/Dumpers/RootDumpers/src/PrTrackerDumper.cpp>`_.
    It was not written by the author of this library.
    """

    output: ResolvedPath
    """Path to the output directory where the resulting ROOT files will be saved.

    This path can contain placeholders like ``{idx}``, which will be resolved
    at runtime based on the chunk being processed.
    """

    digi2root_config_path: ResolvedPath | None = None
    """YAML path for saving the intermediate DIGI2ROOT configuration.

    This path can contain placeholders. If not set, a temporary file is used.
    """

    with_retina_clusters: bool = True
    """Flag indicating whether the input data contains retina clusters."""

    # Private methods ================================================================
    def __get_output_dir(self, placeholders: Mapping[str, str], /) -> Path:
        """Resolve the output directory path using the given placeholders."""
        return (
            Path(self.output.as_posix().format(**placeholders)).expanduser().resolve()
        )

    def __get_digi2root_config_path(
        self, placeholders: Mapping[str, str], temp_dir: Path
    ) -> Path:
        """Resolve the intermediate DIGI2ROOT config path, temporary if not set."""
        digi2root_config_path = self.digi2root_config_path
        if digi2root_config_path is None:
            return temp_dir / "digi2root_config.yaml"

        return (
            Path(resolve_placeholders(digi2root_config_path.as_posix(), placeholders))
            .expanduser()
            .resolve()
        )

    # Implementation of StepBase =====================================================
    @classmethod
    def get_key(cls) -> str:
        """Return the key for this step, ``digi2root``."""
        return "digi2root"

    @classmethod
    def get_chunk_type(cls) -> type:
        """Return the output type for this step, which is a ``Path``."""
        return Path

    # Implementation of MooreStepBase ================================================
    @contextmanager
    def _prepare_moore_config(
        self,
        moore_chunk: MooreChunk,
        xml_catalog_path: Path | None,
        placeholders: Mapping[str, str],
    ) -> Generator[MooreConfig, None, None]:
        """Extend the base Moore config with DIGI2ROOT-specific settings.

        This method prepares the ``DIGI2ROOTConfig``, saves it to a YAML file,
        and adds:

        - The ``digi2root.py`` option file to the Moore config.
        - The ``DIGOUT_DIGI2ROOT_CONFIG_YAML`` environment variable pointing to the
          saved DIGI2ROOT config YAML file.
        """
        from .._moore.digi2root import DIGI2ROOTConfig  # noqa: PLC0415

        output_dir = self.__get_output_dir(placeholders)

        with super()._prepare_moore_config(
            moore_chunk, xml_catalog_path, placeholders
        ) as moore_config:
            digi2root_config = DIGI2ROOTConfig(
                with_retina_clusters=self.with_retina_clusters,
                output_dir=output_dir,
            )
            digi2root_config_path = self.__get_digi2root_config_path(
                placeholders, moore_config.temp_dir
            )
            dump_yaml(
                digi2root_config.model_dump(mode="json"),
                digi2root_config_path.as_posix(),
            )

            option_files = moore_config.option_files
            # Configure the DIGI2ROOT step according to the config
            # in `DIGOUT_DIGI2ROOT_CONFIG_YAML`.
            option_files.append(MOORE_DIR / "digi2root.py")

            environment_variables = moore_config.environment_variables
            environment_variables["DIGOUT_DIGI2ROOT_CONFIG_YAML"] = (
                digi2root_config_path.as_posix()
            )

            yield MooreConfig(
                option_files=option_files,
                temp_dir=moore_config.temp_dir,
                environment_variables=environment_variables,
            )

    def get_target(self, context: Context, /) -> Path:
        """Return the resolved path to the output directory."""
        return self.__get_output_dir(context.placeholders)
