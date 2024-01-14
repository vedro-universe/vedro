from pathlib import Path
from typing import List, Optional, Set

from vedro.core import ScenarioFinder, ScenarioLoader, ScenarioOrderer, VirtualScenario
from vedro.core.scenario_discoverer import ScenarioDiscoverer, create_vscenario

__all__ = ("SelectiveScenarioDiscoverer",)


class SelectiveScenarioDiscoverer(ScenarioDiscoverer):
    def __init__(self,
                 finder: ScenarioFinder, loader: ScenarioLoader, orderer: ScenarioOrderer, *,
                 selected_paths: Optional[Set[Path]] = None) -> None:
        super().__init__(finder, loader, orderer)
        self._selected_paths = selected_paths

    async def discover(self, root: Path) -> List[VirtualScenario]:
        scenarios = []
        async for path in self._finder.find(root):
            if not self._is_path_selected(path):
                continue
            loaded = await self._loader.load(path)
            for scn in loaded:
                scenarios.append(create_vscenario(scn))
        return await self._orderer.sort(scenarios)

    def _is_path_selected(self, path: Path) -> bool:
        if self._selected_paths is None or len(self._selected_paths) == 0:
            return True
        abs_path = path.absolute()
        return any(self._is_relative_to(abs_path, selected) for selected in self._selected_paths)

    def _is_relative_to(self, path: Path, parent: Path) -> bool:
        try:
            path.relative_to(parent)
        except ValueError:
            return False
        else:
            return True
