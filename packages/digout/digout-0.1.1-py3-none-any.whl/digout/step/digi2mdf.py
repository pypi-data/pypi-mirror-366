"""Defines a step that runs the DIGI-to-MDF Moore algorithm."""

from __future__ import annotations

from contextlib import contextmanager
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING

from .._moore.digi2mdf import DIGI2MDFConfig
from .._utils.ioyaml import dump_yaml
from .._utils.path import ResolvedPath  # noqa: TC001 (needed by Pydantic)
from ..step._moore import MooreConfig
from ..stream.digi2mdf import DIGI2MDFChunk
from ..stream.moore import MooreChunk
from ._moore import MOORE_DIR, MooreStepBase

if TYPE_CHECKING:
    from collections.abc import Generator, Mapping

    from ..context import Context
    from ..stream.moore import MooreChunk


logger = getLogger(__name__)


__all__ = ["DIGI2MDFStep"]


class DIGI2MDFStep(MooreStepBase[DIGI2MDFChunk]):
    """Converts DIGI file(s) into a MDF file.

    This step processes raw detector data (DIGI) and converts it into the MDF
    (Moore Data Format), which is often used as input for Allen.
    It extends :py:class:`~digout.step._moore.MooreStepBase` to handle
    the specific configuration for this algorithm.

    The Moore configuration file for this step is based
    on the official configuration file define in the Moore repository,
    at `Moore/Hlt/RecoConf/options/mdf_for_standalone_Allen.py <https://gitlab.cern.ch/lhcb/Moore/-/blob/master/Hlt/RecoConf/options/mdf_for_standalone_Allen.py>`_.
    """

    output: ResolvedPath
    """The path where the output MDF file will be saved.

    This path can contain placeholders like ``{idx}``, which will be resolved
    at runtime based on the chunk being processed.
    """

    geometry_dir: ResolvedPath | None = None
    """The directory where geometry files will be stored.

    This path can also contain placeholders. If not set,
    the geometry files will not be dumped.
    """

    with_retina_clusters: bool = True
    """Flag indicating whether the input data contains retina clusters."""

    digi2mdf_config_path: ResolvedPath | None = None
    """Path for saving the intermediate DIGI2MDF configuration.

    This path can contain placeholders. If not set, a temporary file is used.
    """

    def __get_digi2mdf_config_path(
        self, placeholders: Mapping[str, str], temp_dir: Path
    ) -> Path:
        """Resolve the path for the intermediate DIGI2MDF config file."""
        digi2mdf_config_path = self.digi2mdf_config_path
        if digi2mdf_config_path is None:
            return temp_dir / "digi2mdf_config.yaml"
        return (
            Path(digi2mdf_config_path.as_posix().format(**placeholders))
            .expanduser()
            .resolve()
        )

    def __get_output_path(self, placeholders: Mapping[str, str], /) -> Path:
        """Resolve the output MDF file path using the given placeholders."""
        return Path(self.output.as_posix().format(**placeholders)).resolve()

    def __get_geometry_dir(self, placeholders: Mapping[str, str], /) -> Path | None:
        """Resolve the geometry directory path using the given placeholders."""
        geometry_dir = self.geometry_dir
        if geometry_dir is None:
            return None

        return (
            Path(geometry_dir.as_posix().format(**placeholders)).expanduser().resolve()
        )

    # Implementation of MooreStepBase ================================================
    @contextmanager
    def _prepare_moore_config(
        self,
        moore_chunk: MooreChunk,
        xml_catalog_path: Path | None,
        placeholders: Mapping[str, str],
    ) -> Generator[MooreConfig, None, None]:
        """Extend the base Moore config with DIGI2MDF-specific settings.

        This method prepares the ``DIGI2MDFConfig``, saves it to a YAML file,
        and adds the necessary option file and environment variable to the main
        :py:class:`MooreConfig` object:

        - The ``digi2mdf.py`` option file to the Moore config.
        - The ``DIGOUT_DIGI2MDF_CONFIG_YAML`` environment variable pointing to the
          saved DIGI2MDF config YAML file.
        """
        output_path = self.__get_output_path(placeholders)
        geometry_dir = self.__get_geometry_dir(placeholders)

        with super()._prepare_moore_config(
            moore_chunk, xml_catalog_path, placeholders
        ) as moore_config:
            digi2mdf_config = DIGI2MDFConfig(
                with_retina_clusters=self.with_retina_clusters,
                path=output_path,
                geometry_dir=geometry_dir,
            )
            digi2mdf_config_path = self.__get_digi2mdf_config_path(
                placeholders=placeholders, temp_dir=moore_config.temp_dir
            )
            dump_yaml(
                digi2mdf_config.model_dump(mode="json"),
                digi2mdf_config_path,
            )

            option_files = moore_config.option_files
            # Configure the digi2mdf step using the configuration
            # stored in `DIGOUT_DIGI2MDF_CONFIG_YAML`
            option_files.append(MOORE_DIR / "digi2mdf.py")

            environment_variables = moore_config.environment_variables
            environment_variables["DIGOUT_DIGI2MDF_CONFIG_YAML"] = (
                digi2mdf_config_path.as_posix()
            )

            yield MooreConfig(
                option_files=option_files,
                temp_dir=moore_config.temp_dir,
                environment_variables=environment_variables,
            )

    def get_target(self, context: Context, /) -> DIGI2MDFChunk:
        """Return a ``DIGI2MDFChunk`` object representing the expected output."""
        placeholders = context.placeholders
        output_path = self.__get_output_path(placeholders)
        geometry_dir = self.__get_geometry_dir(placeholders)

        return DIGI2MDFChunk(path=output_path, geometry_dir=geometry_dir)

    # Implementation of StepBase =====================================================
    @classmethod
    def get_key(cls) -> str:
        """Return the key for this step, ``digi2mdf``."""
        return "digi2mdf"

    @classmethod
    def get_chunk_type(cls) -> type:
        """Return :py:class:`~digout.stream.digi2mdf.DIGI2MDFChunk`."""
        return DIGI2MDFChunk
