from types import TracebackType
from typing import Tuple, Type, Union

__all__ = ("catched",)

ExcpectedExcType = Union[Type[BaseException], Tuple[Type[BaseException], ...]]


class catched:
    def __init__(self, expected_exc: ExcpectedExcType = BaseException) -> None:
        assert isinstance(expected_exc, tuple) or issubclass(expected_exc, BaseException)
        self._expected_exc = expected_exc if isinstance(expected_exc, tuple) else (expected_exc,)
        self._type: Union[Type[BaseException], None] = None
        self._value: Union[BaseException, None] = None
        self._traceback: Union[TracebackType, None] = None

    @property
    def type(self) -> Union[Type[BaseException], None]:
        return self._type

    @property
    def value(self) -> Union[BaseException, None]:
        return self._value

    @property
    def traceback(self) -> Union[TracebackType, None]:
        return self._traceback

    def __enter__(self) -> "catched":
        return self

    def __exit__(self,
                 exc_type: Union[Type[BaseException], None],
                 exc_value: Union[BaseException, None],
                 traceback: Union[TracebackType, None]) -> bool:
        if not isinstance(exc_value, self._expected_exc):
            return False
        self._type = exc_type
        self._value = exc_value
        self._traceback = traceback
        return True

    def __repr__(self) -> str:
        return f"<catched exception={self.value!r}>"
