import sys

__all__ = ("context",)

if sys.version_info >= (3, 10):
    from typing import Callable, ParamSpec, TypeVar

    P = ParamSpec("P")
    R = TypeVar("R")

    def context(fn: Callable[P, R]) -> Callable[P, R]:
        setattr(fn, "__vedro__context__", True)
        return fn
else:
    from typing import TypeVar

    T = TypeVar("T")

    def context(fn: T) -> T:
        setattr(fn, "__vedro__context__", True)
        return fn
