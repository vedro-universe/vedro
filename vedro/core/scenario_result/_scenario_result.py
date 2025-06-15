from typing import Any, Dict, List, Union

from vedro.core._artifacts import Artifact
from vedro.core._step_result import StepResult
from vedro.core._virtual_scenario import VirtualScenario

from ._scenario_status import ScenarioStatus

__all__ = ("ScenarioResult",)

ScopeType = Dict[str, Any]


class ScenarioResult:
    """
    Represents the result of a scenario execution.

    This class manages the state and outcome of a scenario, including its status,
    timing, step results, scope, artifacts, and additional details. It provides
    methods to update the status of the scenario, track its execution time, and
    store related data such as artifacts and extra details.
    """

    def __init__(self, scenario: VirtualScenario) -> None:
        """
        Initialize a ScenarioResult instance for the given scenario.

        :param scenario: The virtual scenario for which the result is tracked.
        """
        self._scenario = scenario
        self._status: ScenarioStatus = ScenarioStatus.PENDING
        self._started_at: Union[float, None] = None
        self._ended_at: Union[float, None] = None
        self._step_results: List[StepResult] = []
        self._scope: Union[ScopeType, None] = None
        self._artifacts: List[Artifact] = []
        self._extra_details: List[str] = []

    @property
    def scenario(self) -> VirtualScenario:
        """
        Retrieve the virtual scenario associated with this result.

        :return: The virtual scenario object.
        """
        return self._scenario

    @property
    def status(self) -> ScenarioStatus:
        """
        Retrieve the current status of the scenario.

        :return: The current scenario status.
        """
        return self._status

    def mark_passed(self) -> "ScenarioResult":
        """
        Mark the scenario as passed.

        :return: The ScenarioResult instance for chaining.
        :raises RuntimeError: If the scenario status has already been set.
        """
        if self.status != ScenarioStatus.PENDING:
            raise RuntimeError(
                "Cannot mark scenario as passed because its status has already been set"
            )
        self._status = ScenarioStatus.PASSED
        return self

    def is_passed(self) -> bool:
        """
        Check if the scenario is marked as passed.

        :return: True if the scenario is passed, False otherwise.
        """
        return self._status == ScenarioStatus.PASSED

    def mark_failed(self) -> "ScenarioResult":
        """
        Mark the scenario as failed.

        :return: The ScenarioResult instance for chaining.
        :raises RuntimeError: If the scenario status has already been set.
        """
        if self.status != ScenarioStatus.PENDING:
            raise RuntimeError(
                "Cannot mark scenario as failed because its status has already been set"
            )
        self._status = ScenarioStatus.FAILED
        return self

    def is_failed(self) -> bool:
        """
        Check if the scenario is marked as failed.

        :return: True if the scenario is failed, False otherwise.
        """
        return self._status == ScenarioStatus.FAILED

    def mark_skipped(self) -> "ScenarioResult":
        """
        Mark the scenario as skipped.

        :return: The ScenarioResult instance for chaining.
        :raises RuntimeError: If the scenario status has already been set.
        """
        if self.status != ScenarioStatus.PENDING:
            raise RuntimeError(
                "Cannot mark scenario as skipped because its status has already been set"
            )
        self._status = ScenarioStatus.SKIPPED
        return self

    def is_skipped(self) -> bool:
        """
        Check if the scenario is marked as skipped.

        :return: True if the scenario is skipped, False otherwise.
        """
        return self._status == ScenarioStatus.SKIPPED

    @property
    def started_at(self) -> Union[float, None]:
        """
        Retrieve the timestamp when the scenario started.

        :return: The start time as a float or None if not set.
        """
        return self._started_at

    def set_started_at(self, started_at: float) -> "ScenarioResult":
        """
        Set the start timestamp for the scenario.

        :param started_at: The start time as a float.
        :return: The ScenarioResult instance for chaining.
        """
        self._started_at = started_at
        return self

    @property
    def ended_at(self) -> Union[float, None]:
        """
        Retrieve the timestamp when the scenario ended.

        :return: The end time as a float or None if not set.
        """
        return self._ended_at

    def set_ended_at(self, ended_at: float) -> "ScenarioResult":
        """
        Set the end timestamp for the scenario.

        :param ended_at: The end time as a float.
        :return: The ScenarioResult instance for chaining.
        """
        self._ended_at = ended_at
        return self

    @property
    def elapsed(self) -> float:
        """
        Calculate the elapsed time for the scenario.

        :return: The elapsed time in seconds, or 0.0 if the start or end time is not set.
        """
        if (self._started_at is None) or (self._ended_at is None):
            return 0.0
        return self._ended_at - self._started_at

    def add_step_result(self, step_result: StepResult) -> None:
        """
        Add a step result to the scenario.

        :param step_result: The step result to add.
        """
        self._step_results.append(step_result)

    @property
    def step_results(self) -> List[StepResult]:
        """
        Retrieve the list of step results.

        :return: A shallow copy of the step results list.
        """
        return self._step_results[:]

    def set_scope(self, scope: ScopeType) -> None:
        """
        Set the execution scope for the scenario.

        :param scope: A dictionary representing the execution scope.
        """
        self._scope = scope

    @property
    def scope(self) -> ScopeType:
        """
        Retrieve the execution scope for the scenario.

        :return: A dictionary representing the scope, or an empty dictionary if not set.
        """
        if self._scope is None:
            return {}
        return self._scope

    def attach(self, artifact: Artifact) -> None:
        """
        Attach an artifact to the scenario.

        :param artifact: The artifact to attach.
        :raises TypeError: If the provided artifact is not an instance of Artifact.
        """
        if not isinstance(artifact, Artifact):
            raise TypeError(
                f"Expected an instance of Artifact, got {type(artifact).__name__}"
            )
        self._artifacts.append(artifact)

    @property
    def artifacts(self) -> List[Artifact]:
        """
        Retrieve the list of attached artifacts.

        :return: A shallow copy of the artifacts list.
        """
        # In v2, this will return a tuple instead of a list
        return self._artifacts[:]

    def add_extra_details(self, extra: str) -> None:
        """
        Add extra details related to the scenario.

        :param extra: A string containing additional details.
        """
        self._extra_details.append(extra)

    @property
    def extra_details(self) -> List[str]:
        """
        Retrieve the list of extra details.

        :return: A shallow copy of the extra details list.
        """
        return self._extra_details[:]

    def __repr__(self) -> str:
        """
        Return a string representation of the ScenarioResult instance.

        :return: A string containing the class name, scenario, and status.
        """
        return f"<{self.__class__.__name__} {self._scenario!r} {self._status.value}>"

    def __eq__(self, other: Any) -> bool:
        """
        Check equality with another ScenarioResult instance.

        :param other: The object to compare.
        :return: True if the instances are equal, False otherwise.
        """
        return isinstance(other, self.__class__) and (self.__dict__ == other.__dict__)
