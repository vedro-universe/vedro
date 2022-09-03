from typing import Any, Dict, List, Union

from vedro.core._artifacts import Artifact
from vedro.core._step_result import StepResult
from vedro.core._virtual_scenario import VirtualScenario

from ._scenario_status import ScenarioStatus

__all__ = ("ScenarioResult",)

ScopeType = Dict[str, Any]


class ScenarioResult:
    def __init__(self, scenario: VirtualScenario) -> None:
        self._scenario = scenario
        self._status: ScenarioStatus = ScenarioStatus.PENDING
        self._started_at: Union[float, None] = None
        self._ended_at: Union[float, None] = None
        self._step_results: List[StepResult] = []
        self._scope: Union[ScopeType, None] = None
        self._artifacts: List[Artifact] = []

    @property
    def scenario(self) -> VirtualScenario:
        return self._scenario

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
        return self._step_results[:]

    def set_scope(self, scope: ScopeType) -> None:
        self._scope = scope

    @property
    def scope(self) -> ScopeType:
        if self._scope is None:
            return {}
        return self._scope

    def attach(self, artifact: Artifact) -> None:
        assert isinstance(artifact, Artifact)
        self._artifacts.append(artifact)

    @property
    def artifacts(self) -> List[Artifact]:
        return self._artifacts[:]

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self._scenario!r} {self._status.value}>"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and (self.__dict__ == other.__dict__)
