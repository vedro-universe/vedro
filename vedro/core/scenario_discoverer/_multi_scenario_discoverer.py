import warnings
from pathlib import Path
from typing import List, Optional, Type

from ..._scenario import Scenario
from .._virtual_scenario import VirtualScenario
from .._virtual_step import VirtualStep
from ..scenario_collector._scenario_collector import ScenarioCollector
from ._create_vscenario import create_vscenario
from ._scenario_discoverer import ScenarioDiscoverer

__all__ = ("MultiScenarioDiscoverer",)


class MultiScenarioDiscoverer(ScenarioDiscoverer):
    """
    Discovers and organizes multiple Vedro scenarios.

    Extends the functionality of ScenarioDiscoverer to support the discovery of multiple
    scenarios within a given directory. It uses the 'create_vscenario' function to generate
    VirtualScenario objects and ensures they are properly sorted.
    """

    def _discover_steps(self, scenario: Type[Scenario]) -> List[VirtualStep]:
        """
        Discover steps within a given scenario class.

        This method is deprecated and retained only for backward compatibility. It uses
        'create_vscenario' to generate virtual steps from the scenario.

        :param scenario: The scenario class to discover steps from.
        :return: A list of virtual steps extracted from the scenario.
        :raises DeprecationWarning: Indicates the method is deprecated and should not be used.
        """
        warnings.warn("Deprecated: use create_vscenario instead", DeprecationWarning)
        return create_vscenario(scenario).steps

    async def discover(self, root: Path, *,
                       project_dir: Optional[Path] = None) -> List[VirtualScenario]:
        """
        Discover and organize scenarios from the given root directory.

        Searches for scenario files starting from the root path, loads them as scenario
        objects or virtual scenarios depending on the loader, and then sorts them using
        the configured orderer.

        :param root: The root directory where the scenario discovery begins.
        :param project_dir: The project directory relative to which paths are resolved.
                            Defaults to the parent of the root directory if not provided.
        :return: A list of ordered VirtualScenario objects.
        :raises ValueError: If the number of scenarios returned by the orderer does not
                            match the number of discovered scenarios.
        """
        if project_dir is None:
            # TODO: Make project_dir required in v2.0
            # TODO: Rename root to start_dir in v2.0
            project_dir = root.parent

        scenarios = []
        async for path in self._finder.find(root):
            # Backward compatibility
            if isinstance(self._loader, ScenarioCollector):
                loaded_vscenarios = await self._loader.collect(path, project_dir=project_dir)
                scenarios.extend(loaded_vscenarios)
            else:
                rel_path = path.relative_to(project_dir) if path.is_absolute() else path
                loaded_scenarios = await self._loader.load(rel_path)
                for scn in loaded_scenarios:
                    scenarios.append(create_vscenario(scn, project_dir=project_dir))

        ordered = await self._orderer.sort(scenarios)
        if len(scenarios) != len(ordered):
            raise ValueError(
                f"The scenario orderer returned {len(ordered)} scenario(s), "
                f"but {len(scenarios)} scenario(s) were discovered. "
                "Please ensure the orderer only reorders scenarios without adding or removing any"
            )
        return ordered
