import random
from typing import List

from vedro.core import ScenarioOrderer, VirtualScenario

__all__ = ("RandomOrderer",)


class RandomOrderer(ScenarioOrderer):
    async def sort(self, scenarios: List[VirtualScenario]) -> List[VirtualScenario]:
        copied = scenarios[:]
        random.shuffle(copied)
        return copied
