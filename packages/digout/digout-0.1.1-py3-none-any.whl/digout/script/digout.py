"""Command line interface for digout."""

from __future__ import annotations

from logging import getLogger
from pathlib import Path

import click

from .._utils.debug import DebugHalt
from ..conf import ConfType, copy_init_config_files
from ..config.step import StepConfig
from ..config.workflow import WorkflowConfig
from ._clickutils import CLICK_CONFIG_OPTIONS, CLICK_LOGGING_OPTION

logger = getLogger(__name__)


class _NaturalOrderGroup(click.Group):
    """A Click command group that displays commands in the order they are defined."""

    def list_commands(self, ctx: click.Context) -> list[str]:  # noqa: ARG002
        return list(self.commands)


@click.group(cls=_NaturalOrderGroup)
@CLICK_LOGGING_OPTION
def cli():
    """Command-line interface for the digout library."""


@cli.command()
@click.argument("conftype", type=click.Choice(list(ConfType), case_sensitive=False))
@click.option(
    "-o",
    "--output",
    "output_dir",
    type=click.Path(path_type=Path, dir_okay=True, writable=True, exists=False),
    required=False,
    default=Path.cwd(),
    show_default=True,
    help="Directory to copy the template files into.",
)
@click.option(
    "-f",
    "--force",
    "overwrite",
    is_flag=True,
    default=False,
    help="Overwrite files if they already exist.",
)
def init(conftype: ConfType, output_dir: Path, *, overwrite: bool) -> None:
    """Copy template configuration files to start a new project.

    Depending on CONFTYPE, this command copies one of two bundles of
    template YAML files into the specified output directory:

    - **base**: Copies `default.yaml` and `user.yaml` for project-wide settings.

    - **prod**: Copies `input.yaml` and `root2df.yaml` for a specific production.
    """
    copy_init_config_files(
        conftype=conftype, output_dir=output_dir, overwrite=overwrite
    )


@cli.command()
@CLICK_CONFIG_OPTIONS
@click.option(
    "-i",
    "--chunk-idx",
    type=int,
    default=None,
    required=False,
    help=(
        "Index of a specific chunk to process. "
        "If not provided, only the stream phase is run."
    ),
)
def orchestrate(
    config_paths: list[Path], overrides: list[str], chunk_idx: int | None
) -> None:
    """Run the stream phase and, optionally, orchestrate a single chunk.

    This command merges the provided configuration files into a complete
    `WorkflowConfig`.

    If `--chunk-idx` is not provided, it runs only the stream-level steps.

    If `--chunk-idx` is provided, it runs the stream phase and then immediately
    runs the chunk-level steps for that single chunk,
    which may be useful for debugging.
    """
    workflow_config = WorkflowConfig.create(
        config_paths=config_paths, overrides=overrides
    )
    try:
        if chunk_idx is None:
            # Run the stream phase only
            workflow_config.runner.orchestrate_stream()
        else:
            workflow_config.runner.orchestrate_chunk(chunk_idx)
    except DebugHalt as e:
        logger.debug("Caught DebugHalt: %s", e)


@cli.command()
@CLICK_CONFIG_OPTIONS
def schedule(config_paths: list[Path], overrides: list[str]) -> None:
    """Execute a full workflow from a set of configuration files.

    This is the main command for running a production. It performs the
    following actions:

    1. Merges the provided configuration files and overrides.
    2. Saves the final, resolved `WorkflowConfig` for reproducibility.
    3. Runs the stream phase to prepare the chunks.
    4. Submits all chunks to the configured scheduler for execution.
    """
    workflow_config = WorkflowConfig.create(
        config_paths=config_paths, overrides=overrides
    )
    workflow_config.save_workflow()
    try:
        workflow_config.runner.schedule()
    except DebugHalt as e:
        logger.debug("Caught DebugHalt: %s", e)


@cli.command()
@CLICK_CONFIG_OPTIONS
@click.option(
    "-f",
    "--force",
    "force",
    is_flag=True,
    default=False,
    help="Force execution even if the step is already completed.",
)
def run(config_paths: list[Path], overrides: list[str], *, force: bool) -> None:
    """Execute a single step from a step configuration file.

    This command merges the provided files into a `StepConfig` object and
    executes the defined step in isolation.
    """
    step_config = StepConfig.create(config_paths=config_paths, overrides=overrides)

    if force or not step_config.has_run():
        step_config.run()


@cli.command()
@CLICK_CONFIG_OPTIONS
@click.option(
    "-o",
    "--output",
    "output_path",
    type=click.Path(exists=False, dir_okay=False, writable=True),
    default=None,
    required=False,
    help=(
        "Path to save the workflow configuration. "
        "If not specified, uses the `workflow_path` from the config."
    ),
)
def export(
    config_paths: list[Path], overrides: list[str], output_path: Path | None
) -> None:
    """Merge and export a workflow configuration to a single YAML file.

    This command loads all specified configuration files and overrides,
    resolves all variables and interpolations, and saves the final,
    resolved `WorkflowConfig` to a file.

    This is useful for inspecting the exact configuration before a run or for
    creating a reproducible snapshot of the workflow.
    """
    workflow_config = WorkflowConfig.create(
        config_paths=config_paths, overrides=overrides
    )
    workflow_config.save_workflow(output_path)


if __name__ == "__main__":
    cli()  # pragma: no cover
