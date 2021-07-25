import os
from enum import Enum
from typing import Any, Dict, List, Union

from ._step_result import StepResult
from ._virtual_scenario import VirtualScenario

__all__ = ("ScenarioResult", "ScenarioStatus",)


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
        self._scope: Union[Dict[Any, Any], None] = None

    @property
    def scenario(self) -> VirtualScenario:
        return self._scenario

    @property
    def scenario_subject(self) -> Union[str, None]:
        subject = getattr(self._scenario, "subject", None)
        if isinstance(subject, str) and len(subject) > 0:
            return subject.format(**self._scope) if self._scope else subject
        return self._scenario.path.stem.replace("_", " ")

    @property
    def scenario_namespace(self) -> str:
        namespace = os.path.dirname(os.path.relpath(self._scenario.path, "scenarios"))
        return namespace.replace("_", " ").replace("/", " / ")

    @property
    def status(self) -> ScenarioStatus:
        return self._status

    def mark_passed(self) -> "ScenarioResult":
        self._status = ScenarioStatus.PASSED
        return self

    def is_passed(self) -> bool:
        return self._status == ScenarioStatus.PASSED

    def mark_failed(self) -> "ScenarioResult":
        self._status = ScenarioStatus.FAILED
        return self

    def is_failed(self) -> bool:
        return self._status == ScenarioStatus.FAILED

    def mark_skipped(self) -> "ScenarioResult":
        self._status = ScenarioStatus.SKIPPED
        return self

    def is_skipped(self) -> bool:
        return self._status == ScenarioStatus.SKIPPED

    @property
    def started_at(self) -> Union[float, None]:
        return self._started_at

    def set_started_at(self, started_at: float) -> "ScenarioResult":
        self._started_at = started_at
        return self

    @property
    def ended_at(self) -> Union[float, None]:
        return self._ended_at

    def set_ended_at(self, ended_at: float) -> "ScenarioResult":
        self._ended_at = ended_at
        return self

    @property
    def elapsed(self) -> float:
        if (self._started_at is None) or (self._ended_at is None):
            return 0.0
        return self._ended_at - self._started_at

    def add_step_result(self, step_result: StepResult) -> None:
        self._step_results.append(step_result)

    @property
    def step_results(self) -> List[StepResult]:
        return self._step_results

    def set_scope(self, scope: Dict[Any, Any]) -> None:
        self._scope = scope

    @property
    def scope(self) -> Dict[Any, Any]:
        if self._scope is None:
            return {}
        return self._scope

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._scenario!r})"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and (self.__dict__ == other.__dict__)
