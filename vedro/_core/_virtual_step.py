import inspect
from types import MethodType
from typing import Any, Union


class StepStatus:
    PASSED = "PASSED"
    FAILED = "FAILED"


class VirtualStep:
    def __init__(self, method: MethodType) -> None:
        self._method: MethodType = method
        self._status: Union[str, None] = None

    @property
    def name(self) -> str:
        return self._method.__name__

    def is_coro(self) -> bool:
        return inspect.iscoroutinefunction(self._method)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self._method(*args, **kwargs)

    def mark_passed(self) -> None:
        self._status = StepStatus.PASSED

    def is_passed(self) -> bool:
        return self._status == StepStatus.PASSED

    def mark_failed(self) -> None:
        self._status = StepStatus.FAILED

    def is_failed(self) -> bool:
        return self._status == StepStatus.FAILED
