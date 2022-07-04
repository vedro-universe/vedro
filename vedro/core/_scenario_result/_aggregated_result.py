from typing import List

from vedro.core._virtual_scenario import VirtualScenario

from ._scenario_result import ScenarioResult

__all__ = ("AggregatedResult",)


class AggregatedResult(ScenarioResult):
    def __init__(self, scenario: VirtualScenario) -> None:
        super().__init__(scenario)
        self._scenario_results: List[ScenarioResult] = []

    @property
    def scenario_results(self) -> List[ScenarioResult]:
        return self._scenario_results[:]

    def add_scenario_result(self, scenario_result: ScenarioResult) -> None:
        self._scenario_results.append(scenario_result)

    @staticmethod
    def from_existing(main_scenario_result: ScenarioResult,
                      scenario_results: List[ScenarioResult]) -> "AggregatedResult":
        result = AggregatedResult(main_scenario_result.scenario)

        if main_scenario_result.is_passed():
            result.mark_passed()
        elif main_scenario_result.is_failed():
            result.mark_failed()
        elif main_scenario_result.is_skipped():
            result.mark_skipped()

        if main_scenario_result.started_at is not None:
            result.set_started_at(main_scenario_result.started_at)
        if main_scenario_result.ended_at is not None:
            result.set_ended_at(main_scenario_result.ended_at)

        result.set_scope(main_scenario_result.scope)

        for step_result in main_scenario_result.step_results:
            result.add_step_result(step_result)

        for artifact in main_scenario_result.artifacts:
            result.attach(artifact)

        assert len(scenario_results) > 0
        for scenario_result in scenario_results:
            result.add_scenario_result(scenario_result)

        return result
