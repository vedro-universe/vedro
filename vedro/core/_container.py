from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, Type, TypeVar, Union

from ._plugin import Plugin

__all__ = ("Container", "Factory", "Singleton", "FactoryType", "ConflictError")

F = TypeVar("F")
FactoryType = Union[Type[F], Callable[..., F]]

T = TypeVar("T")


class ConflictError(Exception):
    pass


class Container(Generic[T], ABC):
    def __init__(self, resolver: FactoryType[T]) -> None:
        self._resolver = resolver
        self._initial = resolver
        self._registrant: Union[Plugin, None] = None

    def _make_conflict_error(self, registrant: Plugin) -> ConflictError:
        type_ = self.__orig_class__.__args__[0]  # type: ignore
        return ConflictError(f"{registrant} is trying to register {type_.__name__}, "
                             f"but it is already registered by {self._registrant!r}")

    @abstractmethod
    def register(self, resolver: FactoryType[T], registrant: Plugin) -> None:
        pass

    @abstractmethod
    def resolve(self, *args: Any, **kwargs: Any) -> T:
        pass

    def __call__(self, *args: Any, **kwargs: Any) -> T:
        return self.resolve(*args, **kwargs)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._resolver!r})"


class Factory(Container[T]):
    def register(self, resolver: FactoryType[T], registrant: Plugin) -> None:
        assert isinstance(registrant, Plugin)

        if self._registrant is not None:
            raise self._make_conflict_error(registrant)

        self._resolver = resolver
        self._registrant = registrant

    def resolve(self, *args: Any, **kwargs: Any) -> T:
        return self._resolver(*args, **kwargs)


class Singleton(Container[T]):
    def __init__(self, resolver: FactoryType[T]) -> None:
        super().__init__(resolver)
        self._singleton: Union[None, T] = None

    def register(self, resolver: FactoryType[T], registrant: Plugin) -> None:
        assert isinstance(registrant, Plugin)

        if self._registrant is not None:
            raise self._make_conflict_error(registrant)

        self._resolver = resolver
        self._registrant = registrant

    def resolve(self, *args: Any, **kwargs: Any) -> T:
        if self._singleton is None:
            self._singleton = self._resolver(*args, **kwargs)
        return self._singleton
