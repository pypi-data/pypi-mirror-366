"""Provide the Pydantic models for representing LHCb bookkeeping information.

This package defines a set of structured data models that serve as the schema
for information retrieved from the LHCb Bookkeeping system.

The main model is :py:class:`BKInfo`, which acts as a top-level container for all
other information.

This package also contains the private module ``_dirac``, which allows
to query the LHCb Bookkeeping system via the DIRAC client
to build a :py:class:`BKInfo` object from a given bookkeeping path.
"""

from __future__ import annotations

from ._info import (
    BKInfo,
    FileInfo,
    ProductionConfiguration,
    ProductionInfo,
    ProductionStep,
)

__all__ = [
    "BKInfo",
    "FileInfo",
    "ProductionConfiguration",
    "ProductionInfo",
    "ProductionStep",
]
