import warnings
from pathlib import Path
from typing import List, Type

from ..._scenario import Scenario
from .._virtual_scenario import VirtualScenario
from .._virtual_step import VirtualStep
from ._create_vscenario import create_vscenario
from ._scenario_discoverer import ScenarioDiscoverer

__all__ = ("MultiScenarioDiscoverer",)


class MultiScenarioDiscoverer(ScenarioDiscoverer):
    def _discover_steps(self, scenario: Type[Scenario]) -> List[VirtualStep]:
        # child classes may use this method to discover steps
        warnings.warn("Deprecated: use create_vscenario instead", DeprecationWarning)
        return create_vscenario(scenario).steps

    async def discover(self, root: Path) -> List[VirtualScenario]:
        scenarios = []
        async for path in self._finder.find(root):
            loaded = await self._loader.load(path)
            for scn in loaded:
                scenarios.append(create_vscenario(scn))
        return await self._orderer.sort(scenarios)
