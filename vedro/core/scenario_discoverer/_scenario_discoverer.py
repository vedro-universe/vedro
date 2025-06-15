from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Union

from .._virtual_scenario import VirtualScenario
from ..scenario_collector._scenario_collector import ScenarioCollector
from ..scenario_finder import ScenarioFinder
from ..scenario_loader import ScenarioLoader
from ..scenario_orderer import ScenarioOrderer

__all__ = ("ScenarioDiscoverer",)


class ScenarioDiscoverer(ABC):
    """
    An abstract base class for discovering scenarios.

    This class defines the basic framework for discovering scenarios from a source
    (like a directory). It uses a finder to locate scenarios, a loader to load them,
    and an orderer to sort them into the desired sequence.

    :param finder: An instance of ScenarioFinder for finding scenario files.
    :param loader: An instance of ScenarioLoader for loading scenarios from files.
    :param orderer: An instance of ScenarioOrderer for ordering the loaded scenarios.
    """

    def __init__(self, finder: ScenarioFinder,
                 loader: Union[ScenarioLoader, ScenarioCollector],
                 orderer: ScenarioOrderer) -> None:
        """
        Initialize the ScenarioDiscoverer with necessary components.

        :param finder: An instance of ScenarioFinder to find scenario files.
        :param loader: An instance of ScenarioLoader to load scenarios from files.
        :param orderer: An instance of ScenarioOrderer to order the loaded scenarios.
        """
        # NOTE: Two alternatives are under consideration for v2:
        #   1. Replace the finder with a `DirectoryTraverser` that exposes
        #      async def traverse(self, root: Path) -> AsyncGenerator[Path, None]
        #   2. Introduce a `ScenarioLocator` abstraction with
        #      async def find() -> AsyncIterable[ScenarioSource]
        #      so the discoverer remains agnostic of where scenarios are stored.
        self._finder = finder
        # NOTE: In v2, keep only `ScenarioCollector`; support for `ScenarioLoader`
        #       will be removed.
        self._loader = loader
        self._orderer = orderer

    @abstractmethod
    async def discover(self, root: Path, *,
                       project_dir: Optional[Path] = None) -> List[VirtualScenario]:
        """
        Discover scenarios from a given root path.

        Subclasses should implement this method to define how scenarios are discovered from the
        given root path. The method should return a list of discovered VirtualScenarios.

        :param root: The root path to start discovering scenarios.
        :param project_dir: The project directory to resolve relative paths.
        :return: A list of discovered VirtualScenario instances.
        """
        pass
