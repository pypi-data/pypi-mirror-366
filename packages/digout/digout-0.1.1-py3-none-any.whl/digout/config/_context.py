"""Provides a Pydantic validator for instantiating objects from a context registry."""

from __future__ import annotations

from collections.abc import Mapping
from logging import getLogger
from typing import TYPE_CHECKING, cast

from ..context import Context

if TYPE_CHECKING:
    from pydantic import ValidationInfo

    from ..registry import Registry

logger = getLogger(__name__)


_FIELD_NAME_TO_REGISTRY_NAME: dict[str, str] = {
    "steps": "step",
    "streams": "stream",
    "chunks": "chunk",
    "orchestrators": "orchestrator",
    "schedulers": "scheduler",
}
"""Mapping that connects Pydantic field names to registry names."""


def pydantic_validate_mapping_from_context_registry(
    v: object, info: ValidationInfo
) -> object:
    """Use a context registry to instantiate objects.

    This function is designed to be used with ``@field_validator(..., mode="before")``.
    It takes a dictionary of raw configurations, looks up the appropriate registry
    from the :py:class:`~digout.context.Context` object of the model being validated,
    and then uses that registry to instantiate and validate each item in the dictionary.

    The model using this validator must have a ``context`` field that holds a
    :py:class:`~digout.context.Context` instance. The name of the field being validated
    (e.g., ``steps``) is used to determine which registry to use from the context
    (e.g., the ``step`` registry).

    Args:
        v: The raw input value for the field (expected to be a mapping).
        info: The Pydantic validation info object, used to access the model's
            context and the field's name.

    Returns:
        A new dictionary where the values have been replaced by validated
        instances created by the corresponding registry.

    Raises:
        ValueError: If ``v`` is not a mapping or if the field name is not a
            recognized registry field. This error is caught by Pydantic.
    """
    if not isinstance(v, Mapping):
        msg = (
            "Expected a mapping object, but got "
            f"{type(v).__name__}. Please provide a valid mapping."
        )
        # ValueError for the error to be caught by Pydantic
        raise ValueError(msg)  # noqa: TRY004

    context = info.data.get("context")

    field_name = info.field_name
    assert field_name is not None
    try:
        registry_name = _FIELD_NAME_TO_REGISTRY_NAME[field_name]
    except KeyError as e:
        msg = (
            f"Field '{field_name}' is not a recognized registry field. "
            "Expected one of: " + ", ".join(_FIELD_NAME_TO_REGISTRY_NAME.keys())
        )
        raise ValueError(msg) from e

    assert registry_name is not None
    if context is None:
        logger.debug(
            "No context found in the validation info. Skipping validation for '%s'.",
            registry_name,
        )
        return v

    assert isinstance(context, Context)

    registry = cast(
        "Registry[str, object] | None", context.registries.get(registry_name)
    )
    if registry is None:
        logger.debug(
            "No registry '%s' found in the context. Skipping validation.",
            registry_name,
        )
        return v

    return registry.instantiate_many(v)
