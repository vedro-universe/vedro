from abc import ABC, abstractmethod
from typing import List

from .._virtual_scenario import VirtualScenario

__all__ = ("ScenarioOrderer",)


class ScenarioOrderer(ABC):
    """
    Abstract base class for scenario orderers.

    This class defines the interface for sorting a list of scenarios. Concrete
    implementations of this class should define specific ordering logic.
    """

    @abstractmethod
    async def sort(self, scenarios: List[VirtualScenario]) -> List[VirtualScenario]:
        """
        Sort the given list of scenarios.

        This is an abstract method that must be implemented by subclasses. It should
        return a sorted list of `VirtualScenario` objects based on a specific ordering
        logic.

        :param scenarios: A list of `VirtualScenario` instances to be sorted.
        :return: A new list of `VirtualScenario` instances in the desired order.
        :raises NotImplementedError: If the method is not implemented in a subclass.
        """
        pass
