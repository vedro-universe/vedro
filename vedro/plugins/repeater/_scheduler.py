from typing import List

from vedro.core import AggregatedResult, MonotonicScenarioScheduler, ScenarioResult

__all__ = ("RepeaterScenarioScheduler",)


class RepeaterScenarioScheduler(MonotonicScenarioScheduler):
    def aggregate_results(self, scenario_results: List[ScenarioResult]) -> AggregatedResult:
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
