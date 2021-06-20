import inspect
from pathlib import Path
from typing import Any, List, Tuple, Type

from ..._scenario import Scenario
from .._scenario_finder import ScenarioFinder
from .._scenario_loader import ScenarioLoader
from .._virtual_scenario import VirtualScenario
from .._virtual_step import VirtualStep

__all__ = ("ScenarioDiscoverer",)


class ScenarioDiscoverer:
    def __init__(self, finder: ScenarioFinder, loader: ScenarioLoader) -> None:
        self._finder = finder
        self._loader = loader

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

        def cmp(scn: VirtualScenario) -> Tuple[Any, ...]:
            path = Path(scn.path)
            return (len(path.parts),) + tuple((len(x), x) for x in path.parts)
        scenarios.sort(key=cmp)

        return scenarios
