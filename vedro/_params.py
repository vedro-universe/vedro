from typing import Any, Callable

__all__ = ("params",)


class params:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._args = args
        self._kwargs = kwargs

    def __call__(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        if not hasattr(fn, "__vedro__params__"):
            setattr(fn, "__vedro__params__", [])
        getattr(fn, "__vedro__params__").append((self._args, self._kwargs))
        return fn
