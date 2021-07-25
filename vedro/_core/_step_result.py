from enum import Enum
from typing import Any, Union

from ._exc_info import ExcInfo
from ._virtual_step import VirtualStep

__all__ = ("StepResult", "StepStatus",)


class StepStatus(Enum):
    PENDING = "PENDING"
    PASSED = "PASSED"
    FAILED = "FAILED"


class StepResult:
    def __init__(self, step: VirtualStep) -> None:
        self._step = step
        self._status: StepStatus = StepStatus.PENDING
        self._started_at: Union[float, None] = None
        self._ended_at: Union[float, None] = None
        self._exc_info: Union[ExcInfo, None] = None

    @property
    def step_name(self) -> str:
        return self._step.name

    @property
    def status(self) -> StepStatus:
        return self._status

    def is_passed(self) -> bool:
        return self._status == StepStatus.PASSED

    def is_failed(self) -> bool:
        return self._status == StepStatus.FAILED

    def mark_failed(self) -> "StepResult":
        self._status = StepStatus.FAILED
        return self

    def mark_passed(self) -> "StepResult":
        self._status = StepStatus.PASSED
        return self

    @property
    def started_at(self) -> Union[float, None]:
        return self._started_at

    def set_started_at(self, started_at: float) -> "StepResult":
        self._started_at = started_at
        return self

    @property
    def ended_at(self) -> Union[float, None]:
        return self._ended_at

    def set_ended_at(self, ended_at: float) -> "StepResult":
        self._ended_at = ended_at
        return self

    @property
    def elapsed(self) -> float:
        if (self._started_at is None) or (self._ended_at is None):
            return 0.0
        return self._ended_at - self._started_at

    @property
    def exc_info(self) -> Union[ExcInfo, None]:
        return self._exc_info

    def set_exc_info(self, exc_info: ExcInfo) -> "StepResult":
        self._exc_info = exc_info
        return self

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._step!r})"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and (self.__dict__ == other.__dict__)
