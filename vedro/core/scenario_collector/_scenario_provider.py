from abc import ABC, abstractmethod
from typing import List

from .._virtual_scenario import VirtualScenario
from ._scenario_source import ScenarioSource

__all__ = ("ScenarioProvider",)


class ScenarioProvider(ABC):
    """
    Defines the interface for providing scenarios from a scenario source.

    Implementations of this class extract and return a list of VirtualScenario instances
    based on the given ScenarioSource.
    """

    @abstractmethod
    async def provide(self, source: ScenarioSource) -> List[VirtualScenario]:
        """
        Provide scenarios from the given source.

        :param source: The ScenarioSource object representing the origin of the scenarios.
        :return: A list of VirtualScenario instances discovered in the source.
        """
        pass
