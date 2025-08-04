"""A package that defines the concrete step implementations for the digout framework."""

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, Any, Final, TypeVar

from ..registry import Registry
from .createmoorestream import CreateMooreStreamStep
from .digi2mdf import DIGI2MDFStep
from .digi2root import DIGI2ROOTStep
from .generategridproxy import GenerateGridProxyStep
from .generatexmlcatalog import GenerateXMLCatalogStep
from .root2df import ROOT2DFStep

if TYPE_CHECKING:
    from ..core.step import StepKey
    from .base import StepBase

logger = getLogger(__name__)

__all__ = ["STEP_REGISTRY", "STREAM_REGISTRY", "CHUNK_REGISTRY"]  # noqa: RUF022

V = TypeVar("V")

STEP_REGISTRY: Final[Registry[StepKey, StepBase[Any]]] = Registry(
    name="step", import_path=f"{__name__}.STEP_REGISTRY"
)
"""A registry mapping step keys to step classes.

The following steps are registered:

- **"generate_grid_proxy"**: :py:class:`.GenerateGridProxyStep`: Ensures a valid
  grid proxy is available before running grid-dependent tasks.
- **"create_moore_stream"**: :py:class:`.CreateMooreStreamStep`: Creates a
  ``MooreStream`` of data files from a DIRAC bookkeeping path.
- **"generate_xml_catalog"**: :py:class:`.GenerateXMLCatalogStep`: Generates an
  XML file catalog to map LFNs to PFNs.
- **"digi2root"**: :py:class:`.DIGI2ROOTStep`: Converts DIGI data into ROOT
  files containing particle and hit information.
- **"digi2mdf"**: :py:class:`.DIGI2MDFStep`: Converts DIGI data into MDF
  format for use with tools like Allen.
- **"root2df"**: :py:class:`.ROOT2DFStep`: Converts the ROOT files from the
  `digi2root` step into analysis-friendly dataframes.
"""


STREAM_REGISTRY: Final[Registry[StepKey, object]] = Registry(
    name="stream", import_path=f"{__name__}.STREAM_REGISTRY"
)
"""A registry mapping step keys to the stream types they produce.

This registry is automatically populated by inspecting each step
in :py:data:`STEP_REGISTRY` and registering the type returned
by its :py:meth:`base.StepBase.get_stream_type()` method.
"""


CHUNK_REGISTRY: Final[Registry[StepKey, object]] = Registry(
    name="chunk", import_path=f"{__name__}.CHUNK_REGISTRY"
)
"""A registry mapping step keys to the chunk types they produce.

This registry is automatically populated by inspecting each step
in :py:data:`STEP_REGISTRY` and registering the type returned
by its :py:meth:`base.StepBase.get_chunk_type()` method.
"""

STEP_REGISTRY.register_many(
    [
        # on stream
        GenerateGridProxyStep,
        CreateMooreStreamStep,
        # on stream or chunk
        GenerateXMLCatalogStep,
        # on chunk
        DIGI2ROOTStep,
        DIGI2MDFStep,
        ROOT2DFStep,
    ]
)

logger.debug("Registering streams from steps in the stream registry.")
for step_key, step_cls in STEP_REGISTRY.items():
    try:
        stream_cls: type = step_cls.get_stream_type()
    except NotImplementedError:
        logger.debug(
            "Step %s does not implement get_stream_type()",
            step_cls.get_key(),
        )
    else:
        STREAM_REGISTRY.register(stream_cls, key=step_key)

logger.debug("Registering chunks from steps in the chunk registry.")
for step_key, step_cls in STEP_REGISTRY.items():
    try:
        chunk_cls: type = step_cls.get_chunk_type()
    except NotImplementedError:
        logger.debug(
            "Step %s does not implement get_chunk_type()",
            step_cls.get_key(),
        )
    else:
        CHUNK_REGISTRY.register(chunk_cls, key=step_key)
