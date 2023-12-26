from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Type

from ..._scenario import Scenario

__all__ = ("ScenarioLoader",)


class ScenarioLoader(ABC):
    """
    Abstract base class for a scenario loader.

    This class defines the interface for loading Vedro scenarios. Concrete implementations
    of this class should provide the functionality to load scenarios from a specified source.
    """

    @abstractmethod
    async def load(self, path: Path) -> List[Type[Scenario]]:
        """
        Asynchronously loads Vedro scenarios from a given path.

        This is an abstract method that must be implemented by subclasses. It should
        define how scenarios are loaded from the specified path.

        :param path: The file path or directory from which to load scenarios.
        :return: A list of loaded Vedro scenario classes.
        :raises NotImplementedError: This method should be overridden in subclasses.
        """
        pass
