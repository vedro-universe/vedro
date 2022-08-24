from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, Type, TypeVar, Union

__all__ = ("Container", "Factory", "Singleton", "FactoryType",)

F = TypeVar("F")
FactoryType = Union[Type[F], Callable[..., F]]

T = TypeVar("T")


class Container(Generic[T], ABC):
    def __init__(self, resolver: FactoryType[T]) -> None:
        self._resolver = resolver
        self._default = resolver

    @abstractmethod
    def register(self, resolver: FactoryType[T]) -> None:
        pass

    @abstractmethod
    def resolve(self, *args: Any, **kwargs: Any) -> T:
        pass

    def restore(self) -> None:
        self._resolver = self._default

    def __call__(self, *args: Any, **kwargs: Any) -> T:
        return self.resolve(*args, **kwargs)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._resolver!r})"


class Factory(Container[T]):
    def register(self, resolver: FactoryType[T]) -> None:
        self._resolver = resolver

    def resolve(self, *args: Any, **kwargs: Any) -> T:
        return self._resolver(*args, **kwargs)


class Singleton(Container[T]):
    def __init__(self, resolver: FactoryType[T]) -> None:
        super().__init__(resolver)
        self._singleton: Union[None, T] = None

    def register(self, resolver: FactoryType[T]) -> None:
        self._resolver = resolver

    def resolve(self, *args: Any, **kwargs: Any) -> T:
        if self._singleton is None:
            self._singleton = self._resolver(*args, **kwargs)
        return self._singleton
