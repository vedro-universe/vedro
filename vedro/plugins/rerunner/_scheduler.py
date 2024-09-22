from typing import List

from vedro.core import AggregatedResult, MonotonicScenarioScheduler, ScenarioResult

__all__ = ("RerunnerScenarioScheduler",)


class RerunnerScenarioScheduler(MonotonicScenarioScheduler):
    """
    Custom scenario scheduler that handles the aggregation of rerun scenario results.

    This scheduler aggregates the results of rerun scenario executions. The final
    result is determined based on the majority outcome of the reruns: if more reruns
    passed than failed, the final result will be considered passed, and vice versa.
    """

    def aggregate_results(self, scenario_results: List[ScenarioResult]) -> AggregatedResult:
        """
        Aggregate results from rerun scenario executions into a single result.

        This method processes a list of scenario results and determines the final
        outcome based on the majority of passed or failed rerun attempts. If more
        executions passed than failed, the result will be considered passed,
        otherwise, it will be failed.

        :param scenario_results: A list of `ScenarioResult` instances from rerun executions.
        :return: An aggregated result that summarizes the rerun executions.
        """
        assert len(scenario_results) > 0

        passed, failed = [], []
        for scenario_result in scenario_results:
            if scenario_result.is_passed():
                passed.append(scenario_result)
            elif scenario_result.is_failed():
                failed.append(scenario_result)

        if len(passed) == 0 and len(failed) == 0:
            result = scenario_results[-1]
        else:
            result = passed[-1] if len(passed) > len(failed) else failed[-1]

        return AggregatedResult.from_existing(result, scenario_results)
