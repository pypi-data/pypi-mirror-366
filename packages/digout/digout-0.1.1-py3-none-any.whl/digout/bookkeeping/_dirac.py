"""Provide the :py:func:`get_bk_info_from_bk_path` functions for querying DIRAC.

This module is intended to be run within an active DIRAC environment (e.g., via
``lb-dirac``). It uses the ``LHCbDIRAC`` client to query a bookkeeping path and
returns the results in a structured BKInfo object.
"""

from __future__ import annotations

from logging import getLogger
from typing import Any, NoReturn

from ._info import (
    BKInfo,
    FileInfo,
    ProductionConfiguration,
    ProductionInfo,
    ProductionStep,
)

__all__ = ["get_bk_info_from_bk_path"]

logger = getLogger(__name__)


def _raise_dirac_not_found(exception: Exception) -> NoReturn:
    """Unconditionally raises an ImportError with a message about the DIRAC environment.

    Args:
        exception: The original ``ImportError`` to chain.
    """
    msg = (
        "LHCbDIRAC is not installed. Please use the Dirac environment. "
        "If you have access to CVMFS, after source the LHCb environment, "
        "run the script through ``lb-dirac``."
    )
    raise ImportError(msg) from exception


def __get_configurations_from_production_information(
    production_information: dict[str, Any],
) -> list[ProductionConfiguration]:
    """Parse the 'Production information' key from a raw production info dictionary."""
    configurations = production_information["Production information"]

    production_configurations: list[ProductionConfiguration] = []

    for configuration in configurations:
        if len(configuration) != 3:
            msg = (
                f"Expected configuration to have 3 elements, got {len(configuration)}: "
                f"{configuration}"
            )
            raise ValueError(msg)

        production_configurations.append(
            ProductionConfiguration(
                name=configuration[0],
                version=configuration[1],
                event_type=str(configuration[2]),
            )
        )

    return production_configurations


def __get_steps_from_production_information(
    production_information: dict[str, Any],
) -> list[ProductionStep]:
    """Parse the 'Steps' key from a raw production info dictionary."""
    steps = production_information["Steps"]
    if steps is None:
        return []

    if not isinstance(steps, list):
        msg = f"Expected 'steps' to be a list, got {type(steps).__name__}: {steps}"
        raise TypeError(msg)

    production_steps: list[ProductionStep] = []

    for step in steps:
        if len(step) != 9:
            msg = f"Expected step to have 9 elements, got {len(step)}: {step}"
            raise ValueError(msg)

        production_steps.append(
            ProductionStep(
                step_name=step[0],
                step_id=step[7],
                application_name=step[1],
                application_version=step[2],
                option_files=step[3].split(";"),
                dddb_tag=step[4],
                conddb_tag=step[5],
                extra_packages=step[6],
                visible=step[8],
            )
        )
    return production_steps


def __get_files_from_production_information(
    production_information: dict[str, Any],
) -> list[FileInfo]:
    """Parse the 'Number of events' key from a raw production info dictionary."""
    files = production_information["Number of events"]
    if not files:
        return []

    if not isinstance(files, list):
        msg = f"Expected 'Number of events' to be a list, got {type(files).__name__}"
        raise TypeError(msg)

    file_infos: list[FileInfo] = []

    for file in files:
        if len(file) != 4:
            msg = f"Expected file to have 4 elements, got {len(file)}: {file}"
            raise ValueError(msg)

        file_infos.append(
            FileInfo(
                file_type=file[0],
                n_events=file[1],
                event_type=str(file[2]),
                event_input_stat=file[3],
            )
        )
    return file_infos


def _get_production_info_from_bk_response(
    production_id: int, production_response: dict[str, Any]
) -> ProductionInfo:
    """Parse the raw dictionary from a DIRAC response into a ProductionInfo object.

    Args:
        production_id: The ID of the production being processed.
        production_response: The raw dictionary returned by the DIRAC client's
            ``getProductionInformation`` method.

    Returns:
        A structured py:class:`digout.bookkeeping.ProductionInfo` object.

    Raises:
        RuntimeError: If the DIRAC response indicates a failure.
    """
    logger.info("Processing production information for ID: %d", production_id)
    if not production_response.get("OK"):
        msg = (
            f"Failed to retrieve production information for {production_id}: "
            f"{production_response.get('Message', 'Unknown error')}"
        )
        raise RuntimeError(msg)

    production_information = production_response["Value"]

    return ProductionInfo(
        production_id=production_id,
        configurations=__get_configurations_from_production_information(
            production_information
        ),
        files=__get_files_from_production_information(production_information),
        steps=__get_steps_from_production_information(production_information),
    )


def get_bk_info_from_bk_path(bk_path: str) -> BKInfo:
    """Query the LHCb Bookkeeping system and returns consolidated information.

    This function uses the ``LHCbDIRAC`` client to query for LFNs and production
    metadata associated with a given bookkeeping path.

    Args:
        bk_path: The LHCb Bookkeeping path to query.

    Returns:
        A :py:class:`~digout.bookkeeping.BKInfo` object containing the consolidated
        bookkeeping information.
    """
    try:
        from LHCbDIRAC import __version__ as dirac_version  # noqa: PLC0415
        from LHCbDIRAC.BookkeepingSystem.Client.BKQuery import (  # noqa: PLC0415
            BKQuery,
        )
        from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import (  # noqa: PLC0415
            BookkeepingClient,
        )
    except ImportError as e:
        _raise_dirac_not_found(e)

    logger.debug("Querying LHCb Bookkeeping for path: %s", bk_path)
    bk_query = BKQuery(bk_path)
    bk_query_dict = bk_query.getQueryDict()

    logger.debug("Creating BookkeepingClient instance")
    bk_client = BookkeepingClient()

    logger.info("Retrieving LFNs for path: %s", bk_path)
    lfns = bk_query.getLFNs()
    logger.info("Found %d LFNs", len(lfns))

    logger.info("Retrieving productions for path: %s", bk_path)
    production_ids = bk_query.getBKProductions(bk_path)

    logger.info("Found productions: %s", production_ids)

    production_infos: list[ProductionInfo] = [
        _get_production_info_from_bk_response(
            production_id, bk_client.getProductionInformation(production_id)
        )
        for production_id in production_ids
    ]

    return BKInfo(
        dirac_version=dirac_version,
        runs=bk_query.getBKRuns(),
        config_name=bk_query_dict.get("ConfigName", ""),
        config_version=bk_query_dict.get("ConfigVersion", ""),
        condition=bk_query_dict.get("ConditionDescription", ""),
        event_types=bk_query.getBKEventTypes(),
        file_types=bk_query.getBKFileTypes(),
        bk_path=bk_path,
        lfns=lfns,
        productions=production_infos,
    )
