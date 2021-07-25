from asyncio import iscoroutinefunction
from types import MethodType
from typing import Any

__all__ = ("VirtualStep",)


class VirtualStep:
    def __init__(self, orig_step: MethodType) -> None:
        self._orig_step: MethodType = orig_step

    @property
    def name(self) -> str:
        return self._orig_step.__name__

    def is_coro(self) -> bool:
        return iscoroutinefunction(self._orig_step)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self._orig_step(*args, **kwargs)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._orig_step!r})"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and (self.__dict__ == other.__dict__)
