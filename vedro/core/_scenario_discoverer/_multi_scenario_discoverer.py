import inspect
from pathlib import Path
from typing import List, Type

from ..._scenario import Scenario
from .._virtual_scenario import VirtualScenario
from .._virtual_step import VirtualStep
from ._scenario_discoverer import ScenarioDiscoverer

__all__ = ("MultiScenarioDiscoverer",)


class MultiScenarioDiscoverer(ScenarioDiscoverer):
    def _discover_steps(self, scenario: Type[Scenario]) -> List[VirtualStep]:
        steps = []
        for step in scenario.__dict__:
            if step.startswith("_"):
                continue
            method = getattr(scenario, step)
            if not inspect.isfunction(method):
                continue
            steps.append(VirtualStep(method))
        return steps

    async def discover(self, root: Path) -> List[VirtualScenario]:
        scenarios = []
        async for path in self._finder.find(root):
            loaded = await self._loader.load(path)
            for scn in loaded:
                steps = self._discover_steps(scn)
                scenarios.append(VirtualScenario(scn, steps))
        return await self._orderer.sort(scenarios)
