from typing import List

from .._virtual_scenario import VirtualScenario
from ._scenario_orderer import ScenarioOrderer

__all__ = ("PlainScenarioOrderer",)


class PlainScenarioOrderer(ScenarioOrderer):
    async def sort(self, scenarios: List[VirtualScenario]) -> List[VirtualScenario]:
        return scenarios
