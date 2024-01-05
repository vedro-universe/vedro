from types import TracebackType
from typing import Tuple, Type, Union

__all__ = ("catched",)

ExpectedExcType = Union[Type[BaseException], Tuple[Type[BaseException], ...]]


class catched:
    """
    A context manager for catching and holding exceptions.

    This class is designed to be used in a 'with' statement. It catches exceptions that match the
    specified types and allows the user to inspect them after the block completes.

    For more detailed usage instructions and examples, refer to the Vedro documentation:
    https://vedro.io/docs/guides/testing-exceptions
    """

    def __init__(self, expected_exc: ExpectedExcType = BaseException) -> None:
        """
        Initializes the 'catched' context manager.

        Verifies if the provided `expected_exc` is either a tuple of exceptions or a subclass
        of BaseException.

        :param expected_exc: The exception type(s) to be caught.
        :type expected_exc: ExpectedExcType
        """
        assert isinstance(expected_exc, tuple) or issubclass(expected_exc, BaseException)
        self._expected_exc = expected_exc if isinstance(expected_exc, tuple) else (expected_exc,)
        self._type: Union[Type[BaseException], None] = None
        self._value: Union[BaseException, None] = None
        self._traceback: Union[TracebackType, None] = None

    @property
    def type(self) -> Union[Type[BaseException], None]:
        """
        The type of the caught exception, if any.

        :return: The exception type, or `None` if no exception was caught.
        """
        return self._type

    @property
    def value(self) -> Union[BaseException, None]:
        """
        The caught exception instance, if any.

        :return: The exception instance, or `None` if no exception was caught.
        """
        return self._value

    @property
    def traceback(self) -> Union[TracebackType, None]:
        """
        The traceback associated with the caught exception, if any.

        :return: The traceback, or `None` if no exception was caught.
        """
        return self._traceback

    def __enter__(self) -> "catched":
        """
        Method invoked upon entering the context managed by this context manager.

        :return: The instance of 'catched'.
        """
        return self

    def __exit__(self,
                 exc_type: Union[Type[BaseException], None],
                 exc_value: Union[BaseException, None],
                 traceback: Union[TracebackType, None]) -> bool:
        """
        Method invoked upon exiting the context managed by this context manager.

        This method checks if the raised exception matches the expected exceptions. If it does,
        it captures the exception details and returns True to suppress the exception.

        :param exc_type: The type of the exception raised.
        :param exc_value: The exception instance raised.
        :param traceback: The traceback object associated with the exception.
        :return: True if the exception matches the expected exceptions and is to be handled,
        False otherwise.
        """
        if not isinstance(exc_value, self._expected_exc):
            return False
        self._type = exc_type
        self._value = exc_value
        self._traceback = traceback
        return True

    def __repr__(self) -> str:
        """
        Returns a string representation of the 'catched' instance.

        :return: A string representation, indicating the caught exception, if any.
        """
        return f"<catched exception={self.value!r}>"
