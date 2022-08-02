from types import TracebackType
from typing import Type

__all__ = ("ExcInfo",)


class ExcInfo:
    def __init__(self,
                 type_: Type[BaseException],
                 value: BaseException,
                 traceback: TracebackType) -> None:
        self._type = type_
        self._value = value
        self._traceback = traceback

    @property
    def type(self) -> Type[BaseException]:
        return self._type

    @property
    def value(self) -> BaseException:
        return self._value

    @property
    def traceback(self) -> TracebackType:
        return self._traceback

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._type!r}, {self._value!r}, {self._traceback!r})"
