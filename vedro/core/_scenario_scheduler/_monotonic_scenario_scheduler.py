from collections import OrderedDict
from typing import List, Tuple

from .._scenario_result import ScenarioResult
from .._virtual_scenario import VirtualScenario
from ._scenario_scheduler import ScenarioScheduler

__all__ = ("MonotonicScenarioScheduler",)


class MonotonicScenarioScheduler(ScenarioScheduler):
    def __init__(self, scenarios: List[VirtualScenario]) -> None:
        super().__init__(scenarios)
        self._scheduled = OrderedDict((k, (v, 0)) for k, v in reversed(self._scenarios.items()))
        self._queue: OrderedDict[str, Tuple[VirtualScenario, int]] = OrderedDict()

    def ignore(self, scenario: VirtualScenario) -> None:
        self._scheduled.pop(scenario.unique_id, None)
        self._queue.pop(scenario.unique_id, None)

    def __aiter__(self) -> "ScenarioScheduler":
        self._queue = self._scheduled.copy()
        return super().__aiter__()

    async def __anext__(self) -> VirtualScenario:
        while len(self._queue) > 0:
            _, (scenario, repeats) = self._queue.popitem()
            if repeats > 0:
                self._queue[scenario.unique_id] = (scenario, repeats - 1)
            return scenario
        raise StopAsyncIteration()

    def schedule(self, scenario: VirtualScenario) -> None:
        if scenario.unique_id in self._queue:
            scn, repeats = self._queue[scenario.unique_id]
            scheduled = (scn, repeats + 1)
        else:
            scheduled = (scenario, 0)

        self._scheduled[scenario.unique_id] = scheduled
        self._queue[scenario.unique_id] = scheduled

    def aggregate_results(self, scenario_results: List[ScenarioResult]) -> ScenarioResult:
        assert len(scenario_results) > 0
        for scenario_result in scenario_results:
            if scenario_result.is_failed():
                return scenario_result
        return scenario_results[0]
