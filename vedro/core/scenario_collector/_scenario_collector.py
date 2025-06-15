from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from .._virtual_scenario import VirtualScenario

__all__ = ("ScenarioCollector",)


class ScenarioCollector(ABC):
    """
    Defines the interface for collecting scenarios from a given path.

    Subclasses must implement the 'collect' method to return a list of VirtualScenario
    instances based on the given file path and project directory.
    """

    @abstractmethod
    async def collect(self, path: Path, *, project_dir: Path) -> List[VirtualScenario]:
        """
        Collect virtual scenarios from the specified path.

        :param path: The file path to collect scenarios from.
        :param project_dir: The root directory of the project.
        :return: A list of VirtualScenario objects extracted from the given path.
        """
        pass
