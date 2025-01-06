from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, Type, TypeVar, Union

from ._plugin import Plugin

__all__ = ("Container", "Factory", "Singleton", "FactoryType", "ConflictError")

F = TypeVar("F")
FactoryType = Union[Type[F], Callable[..., F]]

T = TypeVar("T")


class ConflictError(Exception):
    """
    Raised when there is a conflict during the registration of a resolver.

    This exception is raised if a new resolver is attempted to be registered
    when one is already registered by another plugin.
    """
    pass


class Container(Generic[T], ABC):
    """
    Base class for dependency injection containers.

    A container is responsible for managing the creation and resolution of
    objects of a specific type. Subclasses define specific behaviors for
    managing resolvers and handling object creation (e.g., singleton or factory).

    :param resolver: The initial resolver function or type for creating objects.
    """

    def __init__(self, resolver: FactoryType[T]) -> None:
        """
        Initialize the container with the given resolver.

        :param resolver: A callable or type used to create objects of type `T`.
        """
        self._resolver = resolver
        self._initial = resolver
        self._registrant: Union[Plugin, None] = None

    def _make_conflict_error(self, registrant: Plugin) -> ConflictError:
        """
        Create a conflict error indicating a registration conflict.

        :param registrant: The plugin attempting to register the resolver.
        :return: A `ConflictError` with details about the conflicting registration.
        """
        type_ = self.__orig_class__.__args__[0]  # type: ignore
        return ConflictError(f"{registrant} is trying to register {type_.__name__}, "
                             f"but it is already registered by {self._registrant!r}")

    @abstractmethod
    def register(self, resolver: FactoryType[T], registrant: Plugin) -> None:
        """
        Register a new resolver with the container.

        :param resolver: A callable or type used to create objects of type `T`.
        :param registrant: The plugin attempting to register the resolver.
        :raises ConflictError: If another resolver is already registered.
        """
        pass

    @abstractmethod
    def resolve(self, *args: Any, **kwargs: Any) -> T:
        """
        Resolve and return an object of type `T`.

        Subclasses should define how the object is created or retrieved.

        :param args: Positional arguments to pass to the resolver.
        :param kwargs: Keyword arguments to pass to the resolver.
        :return: An instance of type `T`.
        """
        pass

    def __call__(self, *args: Any, **kwargs: Any) -> T:
        """
        Call the container to resolve an object.

        This is a shorthand for calling the `resolve` method.

        :param args: Positional arguments to pass to the resolver.
        :param kwargs: Keyword arguments to pass to the resolver.
        :return: An instance of type `T`.
        """
        return self.resolve(*args, **kwargs)

    def __repr__(self) -> str:
        """
        Return a string representation of the container.

        :return: A string describing the container and its resolver.
        """
        return f"{self.__class__.__name__}({self._resolver!r})"


class Factory(Container[T]):
    """
    A container that creates a new instance of an object each time it is resolved.

    The `Factory` class manages resolvers that are responsible for creating new
    objects of type `T` upon each resolution.
    """

    def register(self, resolver: FactoryType[T], registrant: Plugin) -> None:
        """
        Register a new resolver with the factory.

        :param resolver: A callable or type used to create objects of type `T`.
        :param registrant: The plugin attempting to register the resolver.
        :raises ConflictError: If another resolver is already registered.
        """
        assert isinstance(registrant, Plugin)

        if self._registrant is not None:
            raise self._make_conflict_error(registrant)

        self._resolver = resolver
        self._registrant = registrant

    def resolve(self, *args: Any, **kwargs: Any) -> T:
        """
        Create and return a new instance of type `T`.

        :param args: Positional arguments to pass to the resolver.
        :param kwargs: Keyword arguments to pass to the resolver.
        :return: A new instance of type `T`.
        """
        return self._resolver(*args, **kwargs)


class Singleton(Container[T]):
    """
    A container that ensures a single instance of an object is created and reused.

    The `Singleton` class manages resolvers that are responsible for creating
    objects of type `T`, ensuring that the same instance is returned on each resolution.
    """

    def __init__(self, resolver: FactoryType[T]) -> None:
        """
        Initialize the singleton container with the given resolver.

        :param resolver: A callable or type used to create objects of type `T`.
        """
        super().__init__(resolver)
        self._singleton: Union[None, T] = None

    def register(self, resolver: FactoryType[T], registrant: Plugin) -> None:
        """
        Register a new resolver with the singleton container.

        :param resolver: A callable or type used to create objects of type `T`.
        :param registrant: The plugin attempting to register the resolver.
        :raises ConflictError: If another resolver is already registered.
        """
        assert isinstance(registrant, Plugin)

        if self._registrant is not None:
            raise self._make_conflict_error(registrant)

        self._resolver = resolver
        self._registrant = registrant

    def resolve(self, *args: Any, **kwargs: Any) -> T:
        """
        Resolve and return the singleton instance of type `T`.

        If the singleton instance has not been created yet, it will be created
        using the resolver. Subsequent calls will return the same instance.

        :param args: Positional arguments to pass to the resolver.
        :param kwargs: Keyword arguments to pass to the resolver.
        :return: The singleton instance of type `T`.
        """
        if self._singleton is None:
            self._singleton = self._resolver(*args, **kwargs)
        return self._singleton
