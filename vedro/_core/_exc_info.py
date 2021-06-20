from types import TracebackType
from typing import Type

__all__ = ("ExcInfo",)


class ExcInfo:
    def __init__(self,
                 type_: Type[BaseException],
                 value: BaseException,
                 traceback: TracebackType) -> None:
        self.type = type_
        self.value = value
        self.traceback = traceback

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.type!r}, {self.value!r}, {self.traceback!r})"
