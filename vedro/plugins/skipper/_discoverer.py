from pathlib import Path
from typing import List, Optional, Set

from vedro.core import ScenarioFinder, ScenarioLoader, ScenarioOrderer, VirtualScenario
from vedro.core.scenario_discoverer import ScenarioDiscoverer, create_vscenario

__all__ = ("SelectiveScenarioDiscoverer",)


class SelectiveScenarioDiscoverer(ScenarioDiscoverer):
    """
    Discovers scenarios based on a set of selected paths.

    This class extends `ScenarioDiscoverer` and adds functionality to filter
    scenarios by a predefined set of selected paths. Only scenarios within the
    selected paths are discovered, loaded, and ordered.
    """

    def __init__(self,
                 finder: ScenarioFinder, loader: ScenarioLoader, orderer: ScenarioOrderer, *,
                 selected_paths: Optional[Set[Path]] = None) -> None:
        """
        Initialize the SelectiveScenarioDiscoverer with required components.

        :param finder: The `ScenarioFinder` instance used to find scenario files.
        :param loader: The `ScenarioLoader` instance used to load scenarios.
        :param orderer: The `ScenarioOrderer` instance used to arrange loaded scenarios.
        :param selected_paths: A set of paths to filter scenarios.
                               If None, all scenarios are selected.
        """
        super().__init__(finder, loader, orderer)
        self._selected_paths = selected_paths

    async def discover(self, root: Path, *,
                       project_dir: Optional[Path] = None) -> List[VirtualScenario]:
        """
        Discover scenarios from a root path, filtered by selected paths.

        This method discovers scenarios starting from the specified root path. If
        `selected_paths` is set, only scenarios within those paths are included.
        Scenarios are located, loaded, and ordered before being returned.

        :param root: The root directory from where scenario discovery starts.
        :param project_dir: An optional project directory used for resolving relative paths.
                            Defaults to the parent of the root directory if not provided.
        :return: A list of discovered `VirtualScenario` instances.
        """
        if project_dir is None:
            # TODO: Make project_dir required in v2.0
            project_dir = root.parent

        scenarios = []
        async for path in self._finder.find(root):
            if not self._is_path_selected(path):
                continue
            rel_path = path.relative_to(project_dir) if path.is_absolute() else path
            loaded = await self._loader.load(rel_path)
            for scn in loaded:
                scenarios.append(create_vscenario(scn, project_dir=project_dir))
        return await self._orderer.sort(scenarios)

    def _is_path_selected(self, path: Path) -> bool:
        """
        Check if a given path is within the selected paths.

        This method determines whether a scenario path is included based on
        the `selected_paths` filter.

        :param path: The path to check.
        :return: True if the path is selected, False otherwise.
        """
        if (self._selected_paths is None) or len(self._selected_paths) == 0:
            return True
        abs_path = path.absolute()
        return any(self._is_relative_to(abs_path, selected) for selected in self._selected_paths)

    def _is_relative_to(self, path: Path, parent: Path) -> bool:
        """
        Check if a path is relative to a parent directory.

        This method verifies whether a given path is a subpath of the specified parent directory.

        :param path: The path to check.
        :param parent: The parent directory to check against.
        :return: True if the path is relative to the parent directory, False otherwise.
        """
        try:
            path.relative_to(parent)
        except ValueError:
            return False
        else:
            return True
