from typing import List

from .._virtual_scenario import VirtualScenario
from ._scenario_orderer import ScenarioOrderer

__all__ = ("PlainScenarioOrderer",)


# deprecated
class PlainScenarioOrderer(ScenarioOrderer):
    """
    A simple scenario orderer that preserves the original order of scenarios.

    This orderer does not alter the order of the provided scenarios. It is marked
    as deprecated and may be removed in future versions.
    """

    async def sort(self, scenarios: List[VirtualScenario]) -> List[VirtualScenario]:
        """
        Return the scenarios in their original order.

        :param scenarios: The list of `VirtualScenario` instances to be sorted.
        :return: The same list of scenarios without any modifications.
        """
        return scenarios
