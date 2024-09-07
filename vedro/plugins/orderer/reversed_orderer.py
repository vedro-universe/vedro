from typing import List

from vedro.core import VirtualScenario
from vedro.core.scenario_orderer import StableScenarioOrderer

__all__ = ("ReversedOrderer",)


class ReversedOrderer(StableScenarioOrderer):
    """
    A scenario orderer that reverses the order of scenarios.

    The `ReversedOrderer` reverses the order of the scenarios provided
    by the `StableScenarioOrderer`.
    """

    async def sort(self, scenarios: List[VirtualScenario]) -> List[VirtualScenario]:
        """
        Sort the scenarios in reversed order.

        :param scenarios: The list of `VirtualScenario` instances to be sorted.
        :return: A new list of scenarios in reversed order.
        """
        return list(reversed(await super().sort(scenarios)))
