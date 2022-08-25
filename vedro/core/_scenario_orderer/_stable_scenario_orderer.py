from pathlib import Path
from typing import Any, List, Tuple

from .._virtual_scenario import VirtualScenario
from ._scenario_orderer import ScenarioOrderer

__all__ = ("StableScenarioOrderer",)


class StableScenarioOrderer(ScenarioOrderer):
    async def sort(self, scenarios: List[VirtualScenario]) -> None:
        def cmp(scn: VirtualScenario) -> Tuple[Any, ...]:
            path = Path(scn.path)
            return (len(path.parts),) + tuple((len(x), x) for x in path.parts)

        scenarios.sort(key=cmp)
