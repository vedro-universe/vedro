from types import TracebackType
from typing import Type

__all__ = ("ExcInfo",)


class ExcInfo:
    """
    Represents exception information.

    This class encapsulates the details of an exception, including its type, the exception
    instance itself, and the traceback associated with the exception. It provides a structured
    way to store and access exception details.
    """

    def __init__(self,
                 type_: Type[BaseException],
                 value: BaseException,
                 traceback: TracebackType) -> None:
        """
        Initialize an instance of ExcInfo with exception details.

        :param type_: The type of the exception (e.g., `ValueError`, `TypeError`).
        :param value: The exception instance (i.e., the exception object raised).
        :param traceback: The traceback object associated with the exception, representing
                          the call stack at the point where the exception occurred.
        """
        self.type = type_
        self.value = value
        self.traceback = traceback

    def __repr__(self) -> str:
        """
        Return a string representation of the ExcInfo instance.

        :return: A string containing the exception type, value, and traceback.
        """
        return f"{self.__class__.__name__}({self.type!r}, {self.value!r}, {self.traceback!r})"
