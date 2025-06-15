from typing import List

from vedro.core._virtual_scenario import VirtualScenario

from ._scenario_result import ScenarioResult

__all__ = ("AggregatedResult",)


class AggregatedResult(ScenarioResult):
    """
    Represents an aggregated result of a main scenario and its related scenarios.

    This class extends `ScenarioResult` to include a collection of additional
    scenario results. It is typically used to group the results of a main scenario
    along with its sub-scenarios or related scenarios.
    """

    def __init__(self, scenario: VirtualScenario) -> None:
        """
        Initialize the AggregatedResult with a main scenario.

        :param scenario: The main virtual scenario associated with this aggregated result.
        """
        super().__init__(scenario)
        self._scenario_results: List[ScenarioResult] = []

    @property
    def scenario_results(self) -> List[ScenarioResult]:
        """
        Get the list of aggregated scenario results.

        :return: A list containing all scenario results aggregated in this result.
        """
        return self._scenario_results[:]

    def add_scenario_result(self, scenario_result: ScenarioResult) -> None:
        """
        Add a scenario result to the aggregation.

        :param scenario_result: The scenario result to add to the aggregation.
        """
        self._scenario_results.append(scenario_result)

    @staticmethod
    def from_existing(main_scenario_result: ScenarioResult,
                      scenario_results: List[ScenarioResult]) -> "AggregatedResult":
        """
        Create an `AggregatedResult` instance from an existing main scenario result
        and a list of additional scenario results.

        This method copies all properties (e.g., steps, artifacts, extra details, scope)
        from the main scenario result and aggregates the additional scenario results.
        It also adjusts the `started_at` and `ended_at` timestamps based on the provided
        scenario results.

        :param main_scenario_result: The main scenario result to base the aggregation on.
        :param scenario_results: A list of additional scenario results to aggregate.

        :return: A new `AggregatedResult` instance.
        :raises AssertionError: If the list of `scenario_results` is empty.
        """
        result = AggregatedResult(main_scenario_result.scenario)

        if main_scenario_result.is_passed():
            result.mark_passed()
        elif main_scenario_result.is_failed():
            result.mark_failed()
        elif main_scenario_result.is_skipped():
            result.mark_skipped()

        result.set_scope(main_scenario_result.scope)

        for step_result in main_scenario_result.step_results:
            result.add_step_result(step_result)

        for artifact in main_scenario_result.artifacts:
            result.attach(artifact)

        for extra in main_scenario_result.extra_details:
            result.add_extra_details(extra)

        if len(scenario_results) == 0:
            raise ValueError("No scenario results provided for aggregation")

        for scenario_result in scenario_results:
            if scenario_result.started_at is not None:
                if (result.started_at is None) or (scenario_result.started_at < result.started_at):
                    result.set_started_at(scenario_result.started_at)
            if scenario_result.ended_at is not None:
                if (result.ended_at is None) or (scenario_result.ended_at > result.ended_at):
                    result.set_ended_at(scenario_result.ended_at)

            result.add_scenario_result(scenario_result)

        return result
