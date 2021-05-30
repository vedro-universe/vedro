from types import TracebackType
from typing import Type

__all__ = ("ExcInfo",)


class ExcInfo:
    def __init__(self, type: Type[BaseException],
                 value: BaseException,
                 traceback: TracebackType) -> None:
        self.type = type
        self.value = value
        self.traceback = traceback
