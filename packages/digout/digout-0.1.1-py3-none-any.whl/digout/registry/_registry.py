"""Provides a flexible registry for managing and instantiating types."""

from __future__ import annotations

from collections import UserDict
from collections.abc import Mapping, Sequence
from logging import getLogger
from typing import TYPE_CHECKING, Any, Protocol, Self, TypeVar, cast, runtime_checkable

from pydantic import TypeAdapter, ValidationError
from pydantic_core import core_schema
from typing_extensions import TypedDict

from .._utils.module import import_object

if TYPE_CHECKING:
    from collections.abc import Iterable

    from pydantic import GetCoreSchemaHandler

__all__ = ["Registry", "WithKeyProtocol"]

K = TypeVar("K", bound=str)
"""Type variable for keys in the registry.

Only string keys are allowed.
"""

K_co = TypeVar("K_co", covariant=True)
"""Covariant type variable for keys in the registry."""

V = TypeVar("V")
"""Type variable for values stored in a :class:`Registry`."""


logger = getLogger(__name__)


@runtime_checkable
class WithKeyProtocol(Protocol[K_co]):
    """A protocol for classes that provide a unique key for registration.

    Classes that conform to this protocol can be automatically registered
    to a :py:class:`Registry` without needing to specify an explicit key.

    They must implement the :py:meth:`get_key` classmethod,
    which returns the identifier under which the class will be stored in the registry.
    """

    @classmethod
    def get_key(cls) -> K_co:
        """Return the unique identifier for registering the class."""
        ...


class Registry(UserDict[K, type[V]]):
    """A Pydantic-aware mapping that stores types for later instantiation.

    The registry acts as a central store for types, indexed by unique string keys.
    This allows for decoupling configuration from implementation, as types can be
    referred to by their keys and instantiated with specific data at runtime.

    A :py:class:`Registry` can be used as a Pydantic field type,
    automatically handling serialization to its import path and deserialization
    from an import path back into a :py:class:`Registry` instance.
    """

    def __init__(
        self,
        registry: Mapping[K, type[V]] | None = None,
        /,
        name: str | None = None,
        import_path: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a new Registry instance.

        Args:
            registry: An optional dictionary or mapping to pre-populate the
                registry.
            name: A human-readable name for the registry, used primarily for
                logging. If not provided, the class name is used.
            import_path: The Python import path for this registry instance,
                which is essential for serialization and deserialization.
            **kwargs: Additional keyword arguments to be passed to the underlying
                ``dict`` constructor.
        """
        self.name = name or self.__class__.__name__
        self._import_path = import_path
        super().__init__(registry, **kwargs)

    # Magic methods ==================================================================
    def __setitem__(self, key: K, item: type[V]) -> None:
        """Register a type under a given key, logging a warning on overwrite."""
        logger.debug(
            "Registering '%s' under key '%s' in registry '%s'.", item, key, self.name
        )
        if key in self.data:
            logger.warning(
                "Overwriting existing key '%s' with new value '%s' in registry '%s'.",
                key,
                item,
                self.name,
            )
        super().__setitem__(key, item)

    def __repr__(self) -> str:
        """Return a developer-friendly string representation of the registry."""
        return f"{self.__class__.__name__}<{self.name}>(" + ", ".join(self.keys()) + ")"

    __str__ = __repr__

    # Private methods ================================================================
    def _safe_get(self, key: K, /) -> type[V]:
        """Retrieve a type by key, raising a detailed ``KeyError`` if not found.

        Args:
            key: The key of the type to retrieve.

        Returns:
            The type registered under the specified key.

        Raises:
            KeyError: If the key is not found in the registry.
        """
        try:
            return self.data[key]
        except KeyError as e:
            msg = (
                f"Key {key!r} not found in registry {self.name!r}. "
                "Available keys: " + ", ".join(map(repr, self.data.keys()))
            )
            raise KeyError(msg) from e

    def _filter(self, keys: Iterable[K]) -> dict[K, type[V]]:
        """Filter the registry to a subset containing only the specified keys.

        Args:
            keys: An iterable of keys to select from the registry.

        Returns:
            A new dictionary containing only the key-value pairs for the
            keys that exist in the registry.
        """
        return {key: self._safe_get(key) for key in set(keys)}

    # Public methods =================================================================
    @property
    def import_path(self) -> str:
        """The Python import path of the registry for serialization.

        This path is used to locate and reload the registry from a configuration.

        Raises:
            RuntimeError: If the import path has not been set, as this prevents
                the registry from being serializable.
        """
        if self._import_path is None:
            msg = (
                f"Import path is not set for registry {self.name!r}. "
                "The registry is therefore not serializable."
            )
            raise RuntimeError(msg)
        return self._import_path

    @import_path.setter
    def import_path(self, value: str | None) -> None:
        """Set the Python import path of the registry."""
        self._import_path = value

    def register(self, cls: type[V], /, *, key: K | None = None) -> None:
        """Register a single class in the registry.

        If a ``key`` is not provided, the method attempts to infer it by calling
        the :py:meth:`WithKeyProtocol.get_key` classmethod on ``cls``.

        Args:
            cls: The class (type) to register.
            key: An optional key to register the class under. If provided, it
                must match the key from the class's
                :py:meth:`WithKeyProtocol.get_key` method.

        Raises:
            TypeError: If no key is provided and the class ``cls`` does not
                implement the ``get_key`` classmethod.
            ValueError: If an explicit ``key`` is provided that does not match the
                key returned by the class's ``get_key`` method.
        """
        if isinstance(cls, WithKeyProtocol):
            class_key = cls.get_key()
            if key is not None and class_key != key:
                msg = (
                    f"Class {cls!r} has a different key "
                    f"({class_key!r}) than the provided key ({key!r})."
                )
                raise ValueError(msg)
            key = cast("K", class_key)
        elif key is None:
            msg = (
                f"{cls.__name__} must implement a `get_key` classmethod to be "
                "registered without an explicit key."
            )
            raise TypeError(msg)

        self[key] = cls

    def register_many(self, types: Sequence[type[V]] | Mapping[K, type[V]], /) -> None:
        """Register multiple classes in the registry in a single operation.

        This method can accept either a mapping of keys to classes or a sequence
        of classes that conform to the ``WithKeyProtocol``.

        Args:
            types: A collection of types to register. Can be a mapping of
                ``{key: class}`` or a sequence of classes ``[class1, class2, ...]``.

        Raises:
            TypeError: If ``types`` is not a sequence or mapping, or if a class
                in a sequence does not implement the :py:meth:`WithKeyProtocol.get_key`
                method.
        """
        if isinstance(types, Mapping):
            for key, cls in types.items():
                self.register(cls, key=key)
        elif isinstance(types, Sequence):
            for cls in types:
                self.register(cls)
        else:
            msg = (
                f"Expected a sequence or mapping of types, got {type(types).__name__}."
            )
            raise TypeError(msg)

    def _get_typeddict(
        self, *, keys: Iterable[K] | None = None, total: bool = False
    ) -> type:
        """Create a ``TypedDict`` from the types in the registry.

        This is used internally by :py:mod:`instantiate_many` to create a dynamic
        schema for Pydantic validation.

        Args:
            keys: An optional iterable of keys to include. If ``None``, all items
                in the registry are included.
            total: If ``True``, all keys in the resulting ``TypedDict`` are required.

        Returns:
            A new ``TypedDict`` class.
        """
        items = (
            {key: self._safe_get(key) for key in set(keys)}
            if keys is not None
            else self.data
        )
        name = f"{self.name.capitalize()}TypedDict"
        return TypedDict(name, items, total=total)  # type: ignore[operator]

    def instantiate(self, key: K, value: object, /) -> V:
        """Instantiate an object of the type registered under the given key.

        This method retrieves the type associated with ``key`` and then uses a
        ``pydantic.TypeAdapter`` to validate and coerce the input ``value``
        before passing it to the type's constructor.

        Args:
            key: The registry key of the desired type.
            value: The data to be validated and used for instantiation. This
                is typically a dictionary of constructor arguments.

        Returns:
            A new instance of the registered type, created from the validated
            data.
        """
        type_ = self._safe_get(key)
        return TypeAdapter(type_).validate_python(value)

    def instantiate_many(self, values: Mapping[K, object], /) -> dict[K, V]:
        """Instantiate multiple objects from the registry in a single call.

        This method dynamically creates a ``TypedDict`` from the relevant registry
        entries to perform validation on the entire ``values`` mapping at once.

        Args:
            values: A mapping from registry keys to the data for instantiation.

        Returns:
            A dictionary mapping each key to its newly created instance.

        Raises:
            RuntimeError: If Pydantic validation fails, wrapping the original error.
        """
        typed_dict = self._get_typeddict(keys=values.keys())
        type_adapter = TypeAdapter[dict[K, V]](typed_dict)

        try:
            validated_values = type_adapter.validate_python(values)
        except ValidationError as e:
            msg = (
                f"Error validating an object of the {self.name!r} registry. "
                "The error message is repeated below:\n"
                f"{e}"
            )
            raise RuntimeError(msg) from e

        return validated_values

    # Pydantic integration ===========================================================
    @classmethod
    def _validate(cls, registry_spec: object, /) -> Registry[K, V]:
        """Pydantic validator: converts an import path string into a Registry."""
        if isinstance(registry_spec, str):
            registry = import_object(registry_spec)
            if not isinstance(registry, cls):
                msg = (
                    f"Registry '{registry_spec}' is not "
                    f"a valid {cls.__name__} instance."
                )
                raise TypeError(msg)
        elif isinstance(registry_spec, cls):
            registry = registry_spec
        else:
            msg = f"Invalid registry specification: {registry_spec}."
            raise TypeError(msg)
        return registry

    @classmethod
    def _serialize(cls, registry: Self, /) -> str:
        """Pydantic serializer: converts a Registry into its import path string."""
        return registry.import_path

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _: type[Any], __: GetCoreSchemaHandler, /
    ) -> core_schema.CoreSchema:
        """Define the Pydantic core schema for the Registry class.

        This enables the Registry to be used directly as a type in Pydantic
        models, handling both validation (from an import path string) and
        serialization (to an import path string).
        """
        str_schema = core_schema.str_schema(pattern="^[a-zA-Z_][a-zA-Z0-9_.]*$")
        return core_schema.no_info_plain_validator_function(
            function=cls._validate,
            json_schema_input_schema=str_schema,
            serialization=core_schema.plain_serializer_function_ser_schema(
                function=cls._serialize,
                info_arg=False,
                return_schema=str_schema,
            ),
        )
