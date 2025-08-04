"""Define Pydantic models for LHCb production and bookkeeping information.

These models provide a structured representation of the data retrieved from the
LHCb Bookkeeping system via DIRAC.
"""

from __future__ import annotations

from logging import getLogger
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict

logger = getLogger(__name__)


__all__ = [
    "BKInfo",
    "FileInfo",
    "ProductionConfiguration",
    "ProductionInfo",
    "ProductionStep",
]


class ProductionStep(BaseModel):
    """Represents a single step within an LHCb production."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    step_name: str
    """The name of the production step."""

    step_id: int
    """The unique numerical identifier for this step."""

    application_name: str
    """The name of the application used (e.g., "Boole")."""

    application_version: str
    """The version of the application used (e.g., "v47r0")."""

    option_files: list[str]
    """A list of Gaudi option files associated with this step."""

    dddb_tag: str | None
    """The Detector Description Database (DDDB) tag."""

    conddb_tag: str | None
    """The Conditions Database (CondDB) tag."""

    extra_packages: str | None
    """Any extra software packages required for this step."""

    visible: str
    """The visibility status of the step's output files in the Bookkeeping."""


class ProductionConfiguration(BaseModel):
    """A class to handle configuration information of an LHCb production."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str
    """The name of the production configuration (e.g., "MC", "LHCb")."""

    version: str
    """The version of the production configuration (e.g., "Dev", "Collision25")."""

    event_type: str
    """The event type associated with the configuration.

    For instance, ``30000000`` for min-bias events.
    """


class FileInfo(BaseModel):
    """A class to handle file information in the LHCb Bookkeeping system."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    file_type: str
    """The type of the file (e.g., 'DIGI')."""

    n_events: int
    """The number of events in the file."""

    event_type: str
    """The event type of the file."""

    event_input_stat: int
    # No idea what that is.


class ProductionInfo(BaseModel):
    """A class to handle LHCb production information."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    production_id: int
    """The unique numerical identifier for the production."""

    configurations: list[ProductionConfiguration]
    """A list of configurations used in this production."""

    files: list[FileInfo]
    """A list of file types and event counts for this production."""

    steps: list[ProductionStep]
    """A list of the individual steps that make up this production."""


class BKInfo(BaseModel):
    """The top-level model for all information retrieved from a bookkeeping path.

    This class consolidates all the data associated with a specific DIRAC
    bookkeeping path, including file locations (LFNs) and metadata about the
    productions that generated them.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    bk_path: str
    """The original DIRAC bookkeeping path that was queried."""

    config_name: str
    """The name of the configuration associated with the path (e.g., "MC")."""

    config_version: str
    """The version of the configuration (e.g., "Dev")."""

    condition: str
    """The data-taking condition (e.g., "Beam6800GeV-VeloClosed-MagDown")."""

    runs: list[int] | None
    """A list of run numbers associated with the data."""

    event_types: list[int]
    """A list of event type codes found at this path."""

    file_types: list[str]
    """A list of file types found at this path (e.g., "DIGI")."""

    lfns: list[str]
    """A list of Logical File Names (LFNs) for all data files at this path."""

    productions: list[ProductionInfo]
    """A list of productions associated with the data at this path."""

    dirac_version: str
    """The version of the LHCbDIRAC client used to retrieve this information."""

    _config_name_to_simulation: ClassVar[dict[str, bool]] = {
        "MC": True,
        "LHCb": False,
    }
    """Internal mapping from config name to the 'simulation' flag for Moore."""

    _file_type_to_input_type: ClassVar[dict[str, str]] = {
        "DIGI": "ROOT",
        "XDIGI": "ROOT",
    }
    """Internal mapping from file type to the 'input_type' for Moore."""

    def get_moore_options(self) -> dict[str, Any]:
        """Infer a set of default Moore options from the bookkeeping information.

        This method attempts to determine key Moore configuration parameters
        like ``simulation``, ``input_type``, ``dddb_tag``, and ``conddb_tag`` by
        inspecting the retrieved bookkeeping metadata.

        Returns:
            A dictionary of inferred Moore options.
        """
        moore_options: dict[str, Any] = {}

        # Simulation
        config_name = self.config_name
        if (simulation := self._config_name_to_simulation.get(config_name)) is not None:
            logger.debug(
                "Found simulation flag '%s' for config '%s'", simulation, config_name
            )
            moore_options["simulation"] = simulation
        else:
            logger.debug("No simulation flag found for config '%s'.", config_name)

        # Data type
        if file_types := self.file_types:
            if len(file_types) == 1:
                file_type = file_types[0]
                if (
                    input_type := self._file_type_to_input_type.get(file_type)
                ) is not None:
                    logger.debug(
                        "Found data type '%s' for file type '%s'.",
                        input_type,
                        file_type,
                    )
                    moore_options["input_type"] = input_type
                else:
                    logger.debug("No input type found for file type '%s'.", file_type)
            else:
                logger.debug(
                    "Found multiple file types: %s. Skipping input type setting.",
                    file_types,
                )

        # dddb_tag and conddb_tag
        if (
            (productions := self.productions)
            and (steps := productions[0].steps)
            and (dddb_tag := (step := steps[0]).dddb_tag) is not None
            and (conddb_tag := step.conddb_tag) is not None
        ):
            logger.debug(
                "Found dddb_tag '%s' and conddb_tag '%s' in the first step "
                "of the first production.",
                dddb_tag,
                conddb_tag,
            )
            moore_options["dddb_tag"] = dddb_tag
            moore_options["conddb_tag"] = conddb_tag

        return moore_options
