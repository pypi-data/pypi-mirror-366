"""DataFrame-I/O package.

This sub-package bundles various I/O classes for reading and writing
:py:class:`pandas.DataFrame` objects in different formats:

* **CSV**: via :py:class:`DFCSVPandasIO` (Pandas)
  or :py:class:`DFCSVPyArrowIO` (PyArrow).
* **Parquet**: via :py:class:`DFParquetIO` (PyArrow / Fastparquet).
* **Feather**: via :py:class:`DFFeatherIO` (PyArrow).

For dynamic selection at run-time you can rely on the discriminated union
:py:data:`DFIO`.  Point Pydantic at some user-provided JSON/YAML that contains
``{"type": "parquet", ...}`` and it will materialise the correct concrete
class automatically.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import Discriminator

from ._base import DFIOBase
from ._csv import DFCSVIO, DFCSVPandasIO, DFCSVPyArrowIO
from ._feather import DFFeatherIO
from ._parquet import DFParquetIO

DFIO = Annotated[DFCSVIO | DFParquetIO | DFFeatherIO, Discriminator("type")]
"""Discriminated union of all supported DataFrame I/O classes."""

__all__ = [  # noqa: RUF022
    "DFCSVPandasIO",
    "DFCSVPyArrowIO",
    "DFCSVIO",
    "DFFeatherIO",
    "DFParquetIO",
    "DFIOBase",
]
