from enum import Enum
from typing import List, Union

from ._step_result import StepResult
from ._virtual_scenario import VirtualScenario

__all__ = ("ScenarioResult",)


class ScenarioStatus(Enum):
    PENDING = "PENDING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class ScenarioResult:
    def __init__(self, scenario: VirtualScenario) -> None:
        self._scenario = scenario
        self._status: ScenarioStatus = ScenarioStatus.PENDING
        self._started_at: Union[float, None] = None
        self._ended_at: Union[float, None] = None
        self._step_results: List[StepResult] = []

    def mark_passed(self) -> None:
        self._status = ScenarioStatus.PASSED

    def is_passed(self) -> bool:
        return self._status == ScenarioStatus.PASSED

    def mark_failed(self) -> None:
        self._status = ScenarioStatus.FAILED

    def is_failed(self) -> bool:
        return self._status == ScenarioStatus.FAILED

    def mark_skipped(self) -> None:
        self._status = ScenarioStatus.SKIPPED

    def is_skipped(self) -> bool:
        return self._status == ScenarioStatus.SKIPPED

    @property
    def started_at(self) -> Union[float, None]:
        return self._started_at

    def set_started_at(self, started_at: float) -> None:
        self._started_at = started_at

    @property
    def ended_at(self) -> Union[float, None]:
        return self._ended_at

    def set_ended_at(self, ended_at: float) -> None:
        self._ended_at = ended_at

    def add_step_result(self, step_result: StepResult) -> None:
        self._step_results.append(step_result)

    @property
    def step_results(self) -> List[StepResult]:
        return self._step_results
