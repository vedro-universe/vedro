from typing import List

from vedro.core import VirtualScenario

from .stable_orderer import StableScenarioOrderer

__all__ = ("ReversedOrderer",)


class ReversedOrderer(StableScenarioOrderer):
    async def sort(self, scenarios: List[VirtualScenario]) -> List[VirtualScenario]:
        return list(reversed(await super().sort(scenarios)))
