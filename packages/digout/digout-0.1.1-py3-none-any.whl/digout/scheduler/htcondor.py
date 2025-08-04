"""Provides a scheduler for submitting workflow jobs to an HTCondor cluster."""

from __future__ import annotations

import shlex
from contextlib import contextmanager
from logging import getLogger
from os import getenv
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, Any, ClassVar

from pydantic import Field

from .._utils.logging import LogLevel  # noqa: TC001 (needed by Pydantic)
from .._utils.path import ResolvedPath, create_directory
from ..environment import execute
from ._base import SchedulerBase, get_orchestrate_workflow_args
from ._workflow import get_chunk_indices_to_run

if TYPE_CHECKING:
    from collections.abc import Generator, Iterable

    from ..core.workflow import ChunkWorkflow

__all__ = ["HTCondorScheduler"]

logger = getLogger(__name__)


def _write_condor_file(
    *, config: dict[str, str], items: Iterable[int], path: Path
) -> None:
    """Write an HTCondor submit file with the given configuration.

    Args:
        config: A dictionary of HTCondor parameters.
        items: The indices of the jobs to queue.
        path: The path where the submit file will be written.
    """
    create_directory(path.parent)

    logger.debug("Writing HTCondor submit file to %s", path)
    with path.open("w") as submit_file:
        for key, value in config.items():
            submit_file.write(f"{key} = {value}\n")
        submit_file.write("queue")
        submit_file.write(" 1 in (" + ", ".join([f"{i}" for i in items]) + ")\n")


def _write_bash_script(command: str, script_path: Path) -> None:
    """Write an executable bash script containing the given command.

    The file will be:

    .. code-block:: bash

       #!/bin/bash
       set -e

       <command>

    Args:
        command: The shell command to write into the script.
        script_path: The path where the bash script will be created.
    """
    create_directory(script_path.parent)
    logger.debug("Writing bash script to %s", script_path)
    with script_path.open("w") as script_file:
        script_file.write("#!/bin/bash\n")
        script_file.write("set -e\n\n")
        script_file.write(f"{command}\n")
    script_path.chmod(0o755)  # Make the script executable
    logger.info("Bash script written to %s", script_path)


class HTCondorScheduler(SchedulerBase):
    """A scheduler that submits workflow jobs to an HTCondor cluster.

    This scheduler works by generating two key files:

    1. A bash script (:py:attr:`~HTCondorScheduler.script_path`)
       containing the command to run one chunk.
    2. An HTCondor submit file (:py:attr:`~HTCondorScheduler.submit_path`)
       that executes the script.

    It then calls ``condor_submit`` to add the jobs to the cluster's queue.
    """

    params: dict[str, Any] = Field(default_factory=dict)
    """Additional parameters for the HTCondor submit file.

    Example: ``{"request_cpus": "4", "+MaxRuntime": 3600}``
    """

    submit_path: ResolvedPath | None = None
    """Path for the generated HTCondor submit file.

    If not provided, a temporary file will be created.
    """

    script_path: ResolvedPath
    """Path for the generated bash script that the HTCondor job will run."""

    log_dir: ResolvedPath | None
    """Directory for storing HTCondor log, output, and error files.

    If set, this is used to populate the ``log``, ``output``, and ``error``
    parameters in the submit file. If ``None``, logs will not be saved.
    """

    log_level: LogLevel = "INFO"
    """The logging level for the individual HTCondor jobs."""

    only_missing: bool = True
    """If ``True``, only schedule jobs for chunks with missing outputs."""

    _env_varnames: ClassVar[set[str]] = {"X509_USER_PROXY"}
    """Environment variables from the current session to pass to the job."""

    _env_vars: ClassVar[dict[str, str]] = {
        # Indicates that the job is running on an external server
        "DIGOUT_BATCH_MODE": "1",
    }
    """Fixed environment variables to set for every HTCondor job."""

    @contextmanager
    def _get_submit_path(self) -> Generator[Path, None, None]:
        """Provide a path for the HTCondor submit file, temporary if needed."""
        if self.submit_path is None:
            with TemporaryDirectory() as temp_dir:
                self.submit_path = Path(temp_dir) / "submit.condor"
                yield self.submit_path
        else:
            yield self.submit_path

    def _get_environment_variables(self) -> dict[str, str]:
        """Construct the dictionary of environment variables for the job.

        This includes:

        - Environment variables from the current session specified in
          :py:attr:`HTCondorScheduler._env_varnames`.
        - Fixed environment variables defined in :py:attr:`HTCondorScheduler._env_vars`.
        """
        environment_variables: dict[str, str] = {}
        for varname in self._env_varnames:
            variable = getenv(varname)
            if (variable := getenv(varname)) is not None:
                environment_variables[varname] = variable
                logger.debug(
                    "Setting environment variable '%s' to '%s'", varname, variable
                )
            else:
                logger.warning(
                    "Environment variable '%s' is not set. "
                    "HTCondor job may not work as expected.",
                    varname,
                )

        # Add additional environment variables defined in _env_vars
        for key, value in self._env_vars.items():
            environment_variables[key] = value
            logger.debug("Setting environment variable '%s' to '%s'", key, value)

        return environment_variables

    def _get_command(self, workflow_path: str | Path) -> str:
        """Build the shell command that will be placed in the bash script.

        The ``$1`` is a bash argument that will be replaced by the job's chunk index.
        """
        args = get_orchestrate_workflow_args(
            workflow_path=workflow_path,
            chunk_idx="$1",
            log_level=self.log_level,
        )
        # Join the arguments, quoting them properly
        # do not quote $1, as it will be replaced by $(Item)
        return " ".join(shlex.quote(arg) if arg != "$1" else arg for arg in args)

    def _get_htcondor_params(self, workflow_path: str | Path) -> dict[str, str]:
        """Assembles the complete set of parameters for the HTCondor submit file."""
        params = self.params.copy()

        for key in ["executable", "arguments", "environment", "log", "output", "error"]:
            if key in params:
                del params[key]
                logger.warning(
                    "The '%s' parameter is set in the `params` field, "
                    "but it will be overridden by the workflow configuration. "
                    "Please remove it from the `params` field.",
                    key,
                )

        command = self._get_command(workflow_path)
        script_path = self.script_path
        _write_bash_script(command, script_path)

        params["executable"] = script_path.as_posix()
        params["arguments"] = "$(Item)"
        params["environment"] = (
            '"'
            + " ".join(
                f"{key}={value}"
                for key, value in self._get_environment_variables().items()
            )
            + '"'
        )
        if (log_dir := self.log_dir) is not None:
            create_directory(log_dir)
            params["log"] = log_dir / "htcondor.log"
            params["output"] = log_dir / "stdout_$(Item).log"
            params["error"] = log_dir / "stderr_$(Item).log"
        else:
            logger.warning(
                "No log directory specified. HTCondor logs will not be saved."
            )

        return params

    def _schedule(
        self, workflow_path: str | Path, workflow: ChunkWorkflow[Any, Any]
    ) -> None:
        """Create the necessary HTCondor files and submits the job."""
        htcondor_params = self._get_htcondor_params(workflow_path)

        chunk_indices = (
            get_chunk_indices_to_run(workflow)
            if self.only_missing
            else range(workflow.n_chunks)
        )

        if not chunk_indices:
            logger.info("No chunks to run. Exiting HTCondor scheduler.")
            return

        with self._get_submit_path() as submit_path:
            _write_condor_file(
                config=htcondor_params, items=chunk_indices, path=submit_path
            )
            execute(["condor_submit", submit_path.as_posix()])
        logger.info(
            "HTCondor scheduler submitted the workflow with %d chunks to %s",
            len(chunk_indices),
            submit_path.as_posix(),
        )
        logger.info("You can monitor the job status with 'condor_q' command.")

    @classmethod
    def get_key(cls) -> str:
        """Return the key for this scheduler, ``htcondor``."""
        return "htcondor"
