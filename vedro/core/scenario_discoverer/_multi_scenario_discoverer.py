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
    """
    A class that discovers and organizes multiple Vedro scenarios.

    This class extends ScenarioDiscoverer to handle the discovery of scenarios in a given
    directory and organizes them for further processing. It leverages the functionalities of
    'create_vscenario' for creating virtual scenarios.
    """

    def _discover_steps(self, scenario: Type[Scenario]) -> List[VirtualStep]:
        """
        Discover steps within a given scenario.

        This method is deprecated and should not be used in child classes. It serves as a
        placeholder for compatibility purposes and relies on 'create_vscenario' to discover
        steps in a scenario.

        :param scenario: The scenario class to discover steps from.
        :return: A list of virtual steps extracted from the scenario.
        :raises DeprecationWarning: Indicates the method is deprecated.
        """
        warnings.warn("Deprecated: use create_vscenario instead", DeprecationWarning)
        return create_vscenario(scenario).steps

    async def discover(self, root: Path) -> List[VirtualScenario]:
        """
        Discover and organize scenarios from a specified root path.

        This method iterates through paths found by '_finder', loads scenarios from each path
        using '_loader', and converts them into virtual scenarios with 'create_vscenario'.
        It then sorts the scenarios using '_orderer'.

        :param root: The root path to start the discovery of scenarios.
        :return: A sorted list of virtual scenarios discovered from the root path.
        """
        project_dir = root.parent

        scenarios = []
        async for path in self._finder.find(root):
            loaded = await self._loader.load(path)
            for scn in loaded:
                scenarios.append(create_vscenario(scn, project_dir=project_dir))
        return await self._orderer.sort(scenarios)
