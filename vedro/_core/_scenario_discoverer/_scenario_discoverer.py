from pathlib import Path
from typing import List, Type

from ..._scenario import Scenario
from .._scenario_finder import ScenarioFinder
from .._scenario_loader import ScenarioLoader

__all__ = ("ScenarioDiscoverer",)


class ScenarioDiscoverer:
    def __init__(self, finder: ScenarioFinder, loader: ScenarioLoader) -> None:
        self._finder = finder
        self._loader = loader

    async def discover(self, root: Path) -> List[Type[Scenario]]:
        scenarios = []
        async for path in self._finder.find(root):
            loaded = await self._loader.load(path)
            scenarios += loaded
        return scenarios
