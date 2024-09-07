import random
from typing import List

from vedro.core import ScenarioOrderer, VirtualScenario

__all__ = ("RandomOrderer",)


class RandomOrderer(ScenarioOrderer):
    """
    A scenario orderer that randomizes the order of scenarios.

    The `RandomOrderer` shuffles the provided list of scenarios to execute them in a random order.
    """

    async def sort(self, scenarios: List[VirtualScenario]) -> List[VirtualScenario]:
        """
        Sort the scenarios in random order.

        :param scenarios: The list of `VirtualScenario` instances to be sorted.
        :return: A new list of scenarios in random order.
        """
        copied = scenarios[:]
        random.shuffle(copied)
        return copied
