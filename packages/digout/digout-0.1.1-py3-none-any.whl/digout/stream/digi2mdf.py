"""Define the chunk type for the :py:class:`digout.step.digi2mdf.DIGI2MDFStep` step."""

from __future__ import annotations

from pathlib import Path  # noqa: TC003 (needed by Pydantic)

from pydantic import BaseModel, ConfigDict

__all__ = ["DIGI2MDFChunk"]


class DIGI2MDFChunk(BaseModel):
    """Represent the output of a single DIGI2MDF step execution."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    path: Path
    """The path to the primary output MDF file."""

    geometry_dir: Path | None = None
    """The path to the directory containing associated geometry files.

    ``None`` if no geometry files were produced.
    """
