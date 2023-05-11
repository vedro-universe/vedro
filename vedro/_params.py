from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, Tuple, TypeVar, Union, cast

__all__ = ("params",)


class Parameterized:
    def __init__(self, args: Any, kwargs: Any, decorators: Tuple[Any, ...]) -> None:
        self._args = args
        self._kwargs = kwargs
        self._decorators = decorators

    def __call__(self, fn: Callable[..., None]) -> Callable[..., None]:
        if not hasattr(fn, "__vedro__params__"):
            setattr(fn, "__vedro__params__", [])
        getattr(fn, "__vedro__params__").append((self._args, self._kwargs, self._decorators))
        return fn


T = TypeVar("T")
ItemType = Union[Callable[[T], T], Tuple[Callable[[T], T], ...]]


class Params:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._args = args
        self._kwargs = kwargs

    def __call__(self, fn: Callable[..., None]) -> Callable[..., None]:
        return Parameterized(self._args, self._kwargs, ())(fn)

    def __class_getitem__(cls, item: ItemType[T]) -> Callable[..., Parameterized]:
        decorators = item if isinstance(item, tuple) else (item,)

        @wraps(cls)
        def wrapped(*args: Any, **kwargs: Any) -> Parameterized:
            return Parameterized(args, kwargs, decorators)

        return wrapped


if not TYPE_CHECKING:
    params = Params
else:  # pragma: no cover
    # https://github.com/python/mypy/issues/11501
    # So we have to use TYPE_CHECKING here
    _T = TypeVar("_T")

    class TypedParams:
        def __call__(self, *args: Any, **kwargs: Any) -> Callable[[_T], _T]:
            return cast(Callable[[_T], _T], ...)

        def __getitem__(self, item: ItemType[T]) -> Callable[..., Callable[[_T], _T]]:
            return cast(Callable[..., Callable[[_T], _T]], ...)
    params = TypedParams()
