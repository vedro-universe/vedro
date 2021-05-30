from asyncio import iscoroutinefunction
from types import MethodType
from typing import Any

__all__ = ("VirtualStep",)


class VirtualStep:
    def __init__(self, method: MethodType) -> None:
        self._method: MethodType = method

    @property
    def name(self) -> str:
        return self._method.__name__

    def is_coro(self) -> bool:
        return iscoroutinefunction(self._method)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self._method(*args, **kwargs)

    def __repr__(self) -> str:
        return f"VirtualStep({self._method!r})"
