from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Type

from ..._scenario import Scenario

__all__ = ("ScenarioLoader",)


class ScenarioLoader(ABC):
    """
    Represents an abstract base class for loading scenarios from a given path.

    This class defines an interface for loading scenarios, which should be
    implemented by subclasses to provide specific loading mechanisms.
    """

    @abstractmethod
    async def load(self, path: Path) -> List[Type[Scenario]]:
        """
        Load scenarios from the specified path.

        :param path: The path from which to load scenarios.
        :return: A list of loaded scenarios.
        :raises NotImplementedError: This method should be overridden in subclasses.
        """
        pass
