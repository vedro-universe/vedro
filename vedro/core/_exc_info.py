from types import TracebackType
from typing import Type

__all__ = ("ExcInfo",)


class ExcInfo:
    """
    Represent exception information.

    This class encapsulates the details of an exception, including its type, the exception
    instance itself, and the traceback associated with the exception. It provides a structured
    way to store and access exception information.
    """

    def __init__(self,
                 type_: Type[BaseException],
                 value: BaseException,
                 traceback: TracebackType) -> None:
        """
        Initialize an instance of ExcInfo with exception details.

        :param type_: The type of the exception.
        :param value: The exception instance.
        :param traceback: The traceback object associated with the exception.
        """
        self.type = type_
        self.value = value
        self.traceback = traceback

    def __repr__(self) -> str:
        """
        Return a string representation of the ExcInfo instance.

        :return: A string representation of the ExcInfo instance.
        """
        return f"{self.__class__.__name__}({self.type!r}, {self.value!r}, {self.traceback!r})"
