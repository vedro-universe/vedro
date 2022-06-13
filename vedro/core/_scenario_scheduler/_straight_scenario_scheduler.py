from collections import OrderedDict
from typing import List

from .._virtual_scenario import VirtualScenario
from ._scenario_scheduler import ScenarioScheduler

__all__ = ("StraightScenarioScheduler",)


class StraightScenarioScheduler(ScenarioScheduler):
    def __init__(self, scenarios: List[VirtualScenario]) -> None:
        super().__init__(scenarios)
        self._queue: OrderedDict[str, VirtualScenario] = OrderedDict()

    def ignore(self, scenario: VirtualScenario) -> None:
        super().ignore(scenario)
        self._queue.pop(scenario.unique_id, None)

    def __aiter__(self) -> "StraightScenarioScheduler":
        self._queue = OrderedDict((k, v) for k, v in reversed(self._scenarios.items()))
        return self

    async def __anext__(self) -> VirtualScenario:
        while len(self._queue) > 0:
            _, scenario = self._queue.popitem()
            return scenario
        raise StopAsyncIteration()
