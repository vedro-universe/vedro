from time import time
from types import TracebackType
from typing import Iterator, List, Optional, Type, Union

__all__ = ("given", "when", "then", "Given", "When", "Then", "Step",)


RecordType = tuple[str, str, float, float, Union[BaseException, None]]


class StepRecorder:
    def __init__(self) -> None:
        self._records: List[RecordType] = []

    def record(self, kind: str, name: str, start_at: float, ended_at: float,
               exc: Optional[BaseException] = None) -> None:
        print(f"Recorded {kind} step '{name}' from {start_at} to {ended_at} with exc={exc}")
        self._records.append((kind, name, start_at, ended_at, exc))

    def clear(self) -> None:
        self._records.clear()

    def __iter__(self) -> Iterator[RecordType]:
        return iter(self._records)

    def __len__(self) -> int:
        return len(self._records)


_step_recorder = None


def get_step_recorder() -> StepRecorder:
    global _step_recorder
    if _step_recorder is None:
        _step_recorder = StepRecorder()
    return _step_recorder


class Step:
    """
    Represents a labeled step used to mark a phase of execution.

    This class supports optional naming and can be used as a context manager,
    both synchronously and asynchronously. It is callable to assign a name and
    provides a string representation based on that name.
    """

    def __init__(self, *, step_recorder: Optional[StepRecorder] = None) -> None:
        """
        Initialize the Step with no name set.
        """
        self._name: Union[str, None] = None
        self._started_at: Union[float, None] = None
        self._step_recorder = step_recorder or get_step_recorder()

    def __enter__(self) -> None:
        """
        Enter the synchronous context manager.

        :return: None
        """
        self._started_at = time()

    async def __aenter__(self) -> None:
        """
        Enter the asynchronous context manager.

        :return: None
        """
        return self.__enter__()

    def __exit__(self,
                 exc_type: Optional[Type[BaseException]],
                 exc_val: Optional[BaseException],
                 exc_tb: Optional[TracebackType]) -> bool:
        """
        Exit the synchronous context manager.

        :param exc_type: The type of exception raised, if any.
        :param exc_val: The exception instance raised, if any.
        :param exc_tb: The traceback object, if an exception was raised.
        :return: True if no exception occurred; otherwise False.
        """
        ended_at = time()
        self._step_recorder.record(self.__class__.__name__, self._name or "",
                                   self._started_at or ended_at, ended_at=ended_at, exc=exc_val)

        self._name = None
        self._started_at = None

        return exc_type is None

    async def __aexit__(self,
                        exc_type: Optional[Type[BaseException]],
                        exc_val: Optional[BaseException],
                        exc_tb: Optional[TracebackType]) -> bool:
        """
        Exit the asynchronous context manager.

        :param exc_type: The type of exception raised, if any.
        :param exc_val: The exception instance raised, if any.
        :param exc_tb: The traceback object, if an exception was raised.
        :return: True if no exception occurred; otherwise False.
        """
        return self.__exit__(exc_type, exc_val, exc_tb)

    def __call__(self, name: str) -> "Step":
        """
        Set the name of the step by calling the instance.

        :param name: A string representing the step's name.
        :return: The current Step instance with the name set.
        :raises TypeError: If the provided name is not a string.
        """
        if not isinstance(name, str):
            raise TypeError(f"Step name must be a string, got {type(name)}")
        self._name = name
        return self

    def __repr__(self) -> str:
        """
        Return a string representation of the step.

        :return: A string representing the step class and its name (if set).
        """
        if self._name is None:
            return f"<{self.__class__.__name__}>"
        return f"<{self.__class__.__name__} name={self._name!r}>"


class Given(Step):
    """
    Represents a setup or preparation step.

    Use this to label a phase where initial conditions are established.
    """
    pass


class When(Step):
    """
    Represents an action or triggering step.

    Use this to label a phase where the main activity is performed.
    """
    pass


class Then(Step):
    """
    Represents a verification or result-checking step.

    Use this to label a phase where outcomes are examined or validated.
    """
    pass


given = Given()
"""
An instance representing a setup or preparation step.
"""

when = When()
"""
An instance representing an action or triggering step.
"""

then = Then()
"""
An instance representing a verification or result-checking step.
"""
