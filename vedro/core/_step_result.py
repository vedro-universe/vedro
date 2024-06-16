from enum import Enum
from typing import Any, List, Union

from ._artifacts import Artifact
from ._exc_info import ExcInfo
from ._virtual_step import VirtualStep

__all__ = ("StepResult", "StepStatus",)


class StepStatus(Enum):
    """
    Enumeration of possible states for `StepResult` to indicate the current status
    of a test step.

    For more information, refer to https://vedro.io/docs/core/step-status.
    """

    # Indicates the step is awaiting execution.
    PENDING = "PENDING"

    # Signifies the step has completed successfully.
    PASSED = "PASSED"

    # Marks the step as unsuccessful due to an assertion failure or an unexpected error.
    FAILED = "FAILED"


class StepResult:
    def __init__(self, step: VirtualStep) -> None:
        self._step = step
        self._status: StepStatus = StepStatus.PENDING
        self._started_at: Union[float, None] = None
        self._ended_at: Union[float, None] = None
        self._exc_info: Union[ExcInfo, None] = None
        self._artifacts: List[Artifact] = []
        self._extra_details: List[str] = []

    @property
    def step(self) -> VirtualStep:
        return self._step

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
        if self._status != StepStatus.PENDING:
            raise RuntimeError(
                "Cannot mark step as failed because its status has already been set")
        self._status = StepStatus.FAILED
        return self

    def mark_passed(self) -> "StepResult":
        if self._status != StepStatus.PENDING:
            raise RuntimeError(
                "Cannot mark step as passed because its status has already been set")
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

    def attach(self, artifact: Artifact) -> None:
        if not isinstance(artifact, Artifact):
            raise TypeError("artifact must be an instance of Artifact")
        self._artifacts.append(artifact)

    @property
    def artifacts(self) -> List[Artifact]:
        return self._artifacts[:]

    def add_extra_details(self, extra: str) -> None:
        self._extra_details.append(extra)

    @property
    def extra_details(self) -> List[str]:
        return self._extra_details[:]

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self._step!r} {self._status.value}>"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and (self.__dict__ == other.__dict__)
