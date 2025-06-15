from typing import List

from vedro.core import AggregatedResult, MonotonicScenarioScheduler, ScenarioResult

__all__ = ("RepeaterScenarioScheduler",)


class RepeaterScenarioScheduler(MonotonicScenarioScheduler):
    """
    Custom scenario scheduler that handles the aggregation of repeated scenario results.

    This scheduler aggregates results of repeated scenario executions. It ensures that
    the final result reflects the failure of any individual execution, while capturing
    all attempts for reporting purposes.
    """

    def aggregate_results(self, scenario_results: List[ScenarioResult]) -> AggregatedResult:
        """
        Aggregate results from repeated scenario executions into a single result.

        This method processes a list of scenario results and determines the final
        outcome based on whether any scenario execution failed. The last failed result
        is returned if any failures occurred, otherwise the last passed result.

        :param scenario_results: A list of `ScenarioResult` instances from repeated executions.
        :return: An aggregated result that summarizes the repeated executions.
        """
        assert len(scenario_results) > 0

        passed, failed = [], []
        for scenario_result in scenario_results:
            if scenario_result.is_passed():
                passed.append(scenario_result)
            elif scenario_result.is_failed():
                failed.append(scenario_result)

        if len(passed) == 0 and len(failed) == 0:
            scenario_result = scenario_results[-1]
        else:
            scenario_result = failed[-1] if len(failed) > 0 else passed[-1]

        return AggregatedResult.from_existing(scenario_result, scenario_results)
