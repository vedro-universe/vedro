from typing import TypeVar

__all__ = ("context",)

T = TypeVar("T")


def context(fn: T) -> T:
    return fn
