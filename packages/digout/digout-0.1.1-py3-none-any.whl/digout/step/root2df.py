"""Defines a step that converts ROOT files into dataframes."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .._utils.format import partial_format
from .._utils.path import ResolvedPath  # noqa: TC001 (needed by Pydantic)
from ..dfio import DFIO  # noqa: TC001 (needed by Pydantic)
from ..root2df import DFNAMES, DFName, root2df
from .base import StepBase

if TYPE_CHECKING:
    from ..context import Context
    from ..core.step import StepKey

__all__ = ["ROOT2DFStep"]

logger = getLogger(__name__)


def _resolve_path_to_dict(path: str, dfnames: Iterable[DFName]) -> dict[DFName, str]:
    """Expand a path template into a dictionary of paths for each dataframe name.

    Args:
        path: The path template to expand,
            which must contain the placeholder ``{dfname}``.
        dfnames: An iterable of dataframe names to use for expansion.

    Returns:
        A dictionary mapping each dataframe name to its corresponding path.
    """
    if "{dfname}" not in path:
        msg = (
            f"Output path template '{path}' does not contain the '{{dfname}}' "
            "placeholder. "
            "This placeholder is required to specify the DataFrame name."
        )
        raise ValueError(msg)
    return {dfname: partial_format(path, dfname=dfname) for dfname in dfnames}


def _resolve_wpath_to_path(
    path: str | Path, placeholders: Mapping[str, Any], dfio: DFIO
) -> Path:
    """Resolve a path template with placeholders and adds a file extension.

    This function first applies the runtime placeholders (like ``{idx}``) and then
    ensures the path has the correct file extension based on the
    `:py:mod:`~digout.dfio` backend.

    Args:
        path: The path template to resolve.
        placeholders: A mapping of runtime placeholders to their values.
        dfio: The dataframe I/O handler, used to determine the file extension.

    Returns:
        The fully resolved, absolute path.
    """
    path = Path(partial_format(str(path), **placeholders))
    if not path.suffix:
        path = dfio.add_extension(path)
    return path.resolve()


class ROOT2DFStep(StepBase[dict[DFName, Path]]):
    """Converts the output of the :py:class:`~digout.step.digi2root.DIGI2ROOTStep` step into dataframes.

    This step reads the output of a :py:class:`~digout.step.digi2root.DIGI2ROOTStep`
    and processes the ROOT files to create structured dataframes,
    which are then saved to disk in a specified format (e.g., CSV, Parquet).
    """  # noqa: E501

    output: dict[DFName, ResolvedPath] | ResolvedPath
    """The output path(s) for the generated dataframe files.

    This can be either:

    1. A single path string containing the ``{dfname}`` placeholder, which will
       be expanded for each dataframe produced (e.g., ``output/{dfname}.csv``).
    2. A dictionary mapping each dataframe name directly to its output path.

    Paths can also contain other runtime placeholders like ``{idx}``. The file
    extension is optional and will be added automatically based
    on the :py:mod:`~digout.dfio` backend used.
    """

    dfio: DFIO
    """The dataframe I/O backend used for saving the dataframes."""

    dfname_to_columns: dict[DFName, list[str] | None] | None = None
    """Specifies which dataframes to create and which columns to include.

    If a dataframe name from :py:data:`step.root2df.DFNAMES` is not a key in this
    dictionary, it will not be produced.

    If a key's value is ``None``, all available columns for that dataframe will be
    included.

    If this field is set to ``None``, all dataframes will be produced with all
    available columns.
    """

    # Private methods ================================================================
    @property
    def _dfname_to_wpath(self) -> dict[DFName, str]:
        """Return a dictionary mapping each dataframe name to its path template."""
        output = self.output
        if isinstance(output, Path):
            return _resolve_path_to_dict(output.as_posix(), self.dfnames)
        elif isinstance(output, Mapping):
            return {dfname: output[dfname].as_posix() for dfname in self.dfnames}
        else:  # pragma: no cover (should ne be reachable)
            msg = (
                f"Invalid output type: {type(self.output)}. "
                "Expected a string or a mapping from DFName to str."
            )
            raise TypeError(msg)

    def _parse_sources(self, sources: Mapping[StepKey, object], /) -> Path:
        """Extract the input ROOT file directory from the step's sources."""
        source = sources["digi2root"]
        if not isinstance(source, Path):
            msg = (
                f"Expected source 'digi2root' to be of type Path, "
                f"but got {type(source)}. "
                "This step requires the output of the DIGI2ROOT step."
            )
            raise TypeError(msg)
        return source

    # Implementation of StepBase =====================================================
    def _run(
        self, sources: Mapping[StepKey, object], context: Context, /
    ) -> dict[DFName, Path]:
        """Execute the ROOT2DF conversion."""
        input_dir = self._parse_sources(sources)
        # Resolve output paths
        dfname_to_path = self.get_dfname_to_path(context.placeholders)

        # Run
        root2df(
            input_dir=input_dir,
            dfname_to_output_path=dfname_to_path,
            dfio=self.dfio,
            dfname_to_columns=self.dfname_to_columns,
        )

        return dfname_to_path

    @classmethod
    def get_chunk_type(cls) -> type:
        """Return the output type for this step."""
        return dict[DFName, Path]

    def get_target(self, context: Context, /) -> dict[DFName, Path]:
        """Return a dictionary of the final, resolved output paths.

        The dictionary maps each dataframe name to its corresponding output path,
        resolved using the current context's placeholders.
        """
        return self.get_dfname_to_path(context.placeholders)

    @classmethod
    def get_key(cls) -> str:
        """Return the key for this step, ``root2df``."""
        return "root2df"

    def get_source_keys(self) -> set[str]:
        """Return the set of step keys this step depends on.

        :py:class:`"digi2root" <digout.step.digi2root.DIGI2ROOTStep>`
        """
        return {"digi2root"}

    # Public methods =================================================================
    @property
    def dfnames(self) -> set[DFName]:
        """The set of dataframe names that this step will produce."""
        if self.dfname_to_columns is None:
            return DFNAMES
        return set(self.dfname_to_columns.keys())

    def get_dfname_to_path(self, placeholders: Mapping[str, Any]) -> dict[DFName, Path]:
        """Construct the final, resolved output paths for each dataframe."""
        return {
            dfname: _resolve_wpath_to_path(output_wpath, placeholders, self.dfio)
            for dfname, output_wpath in self._dfname_to_wpath.items()
        }
