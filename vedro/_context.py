from typing import TypeVar

__all__ = ("context",)

T = TypeVar("T")


def context(fn: T) -> T:
    setattr(fn, "__vedro__context__", True)
    return fn
