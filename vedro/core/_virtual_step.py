from asyncio import iscoroutinefunction
from typing import Any, Callable

__all__ = ("VirtualStep",)


class VirtualStep:
    """
    Represents a virtual step in a scenario.

    This class wraps a callable step, providing methods to check if the step is asynchronous
    and to execute the step.
    """

    def __init__(self, orig_step: Callable[..., None]) -> None:
        """
        Initialize the VirtualStep instance with the original step.

        :param orig_step: The original callable step to be wrapped.
        """
        self._orig_step = orig_step

    @property
    def name(self) -> str:
        """
        Get the name of the original step.

        :return: A string representing the name of the original step.
        """
        return self._orig_step.__name__

    def is_coro(self) -> bool:
        """
        Check if the original step is a coroutine function.

        :return: A boolean indicating if the original step is a coroutine function.
        """
        return iscoroutinefunction(self._orig_step)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """
        Execute the original step with the provided arguments and keyword arguments.

        :param args: Positional arguments to pass to the original step.
        :param kwargs: Keyword arguments to pass to the original step.
        :return: The result of executing the original step.
        """
        return self._orig_step(*args, **kwargs)

    def __repr__(self) -> str:
        """
        Return a string representation of the VirtualStep instance.

        :return: A string representing the VirtualStep instance.
        """
        return f"<{self.__class__.__name__} {self._orig_step.__name__!r}>"

    def __eq__(self, other: Any) -> bool:
        """
        Check equality with another object.

        :param other: The other object to compare with.
        :return: A boolean indicating if the other object is equal to this instance.
        """
        return isinstance(other, self.__class__) and (self.__dict__ == other.__dict__)
