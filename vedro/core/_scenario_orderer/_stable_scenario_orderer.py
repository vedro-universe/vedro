from pathlib import Path
from typing import Any, List, Tuple

from .._virtual_scenario import VirtualScenario
from ._scenario_orderer import ScenarioOrderer

__all__ = ("StableScenarioOrderer",)


class StableScenarioOrderer(ScenarioOrderer):
    def _cmp(self, scn: VirtualScenario) -> Tuple[Any, ...]:
        path = Path(scn.path)
        return (len(path.parts),) + tuple((len(x), x) for x in path.parts)

    async def sort(self, scenarios: List[VirtualScenario]) -> List[VirtualScenario]:
        return list(sorted(scenarios, key=self._cmp))
