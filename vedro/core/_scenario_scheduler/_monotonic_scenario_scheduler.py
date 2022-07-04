from collections import OrderedDict
from typing import Iterator, List, Tuple

from .._scenario_result import AggregatedResult, ScenarioResult
from .._virtual_scenario import VirtualScenario
from ._scenario_scheduler import ScenarioScheduler

__all__ = ("MonotonicScenarioScheduler",)


class MonotonicScenarioScheduler(ScenarioScheduler):
    def __init__(self, scenarios: List[VirtualScenario]) -> None:
        super().__init__(scenarios)
        self._scheduled = OrderedDict((k, (v, 0)) for k, v in reversed(self._discovered.items()))
        self._queue: OrderedDict[str, Tuple[VirtualScenario, int]] = OrderedDict()

    @property
    def scheduled(self) -> Iterator[VirtualScenario]:
        for scenario_id in reversed(self._scheduled):
            scenario, repeats = self._scheduled[scenario_id]
            for _ in range(repeats + 1):
                yield scenario

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
        if scenario.unique_id in self._scheduled:
            scn, repeats = self._scheduled[scenario.unique_id]
            scheduled = (scn, repeats + 1)
        else:
            scheduled = (scenario, 0)
        self._scheduled[scenario.unique_id] = scheduled

        if scenario.unique_id in self._queue:
            scn, repeats = self._queue[scenario.unique_id]
            queued = (scn, repeats + 1)
        else:
            queued = (scenario, 0)
        self._queue[scenario.unique_id] = queued

    def aggregate_results(self, scenario_results: List[ScenarioResult]) -> AggregatedResult:
        assert len(scenario_results) > 0

        result = scenario_results[0]
        for scenario_result in scenario_results:
            if scenario_result.is_failed():
                result = scenario_result
                break

        return AggregatedResult.from_existing(result, scenario_results)
