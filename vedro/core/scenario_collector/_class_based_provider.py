import os
from inspect import isclass
from types import ModuleType
from typing import Any, List, Type

from vedro.core import VirtualScenario
from vedro.core.scenario_discoverer import create_vscenario

from ..._scenario import Scenario
from ._scenario_provider import ScenarioProvider
from ._scenario_source import ScenarioSource

__all__ = ("ClassBasedProvider",)


class ClassBasedProvider(ScenarioProvider):
    async def provide(self, source: ScenarioSource) -> List[VirtualScenario]:
        module = await source.get_module()
        scenarios = self._collect_scenarios(module)
        return [create_vscenario(scn, project_dir=source.project_dir) for scn in scenarios]

    def _collect_scenarios(self, module: ModuleType) -> List[Type[Scenario]]:
        """
        Collect scenarios from the given module.

        :param module: The module from which to collect scenarios.
        :return: A list of collected scenarios.
        """
        loaded = []

        # Iterate over the module's dictionary because it preserves the order of definitions,
        # which is not guaranteed when using dir(module)
        for name, val in module.__dict__.items():
            # Skip private and special attributes
            if name.startswith("_"):
                continue

            # Skip scenarios defined in other modules
            if getattr(val, "__module__", None) != module.__name__:
                continue

            # Check if the value is a Vedro scenario
            if self._is_vedro_scenario(val):
                val.__file__ = os.path.abspath(module.__file__)  # type: ignore
                loaded.append(val)

        return loaded

    def _is_vedro_scenario(self, val: Any) -> bool:
        """
        Check if the given value is a Vedro scenario.

        :param val: The value to check.
        :return: True if the value is a Vedro scenario, False otherwise.
        :raises TypeError: If a class name suggests it's a scenario, but
                           it doesn't inherit from `vedro.Scenario`.
        """

        # First, check if 'val' is a class. Non-class values are not scenarios
        if not isclass(val):
            return False

        cls_name = val.__name__

        # Exclude the foundational 'Scenario' class and 'VedroTemplate',
        # as these are not user-defined scenario classes
        if (val == Scenario) or (cls_name == "VedroTemplate"):
            return False

        # Check if 'val' is a subclass of Vedro's Scenario class
        if issubclass(val, Scenario):
            return True

        # Raise an error if a class name suggests it's a scenario, but
        # it doesn't inherit from Vedro.Scenario
        if cls_name.startswith("Scenario") or cls_name.endswith("Scenario"):
            if len(val.__bases__) == 1 and val.__bases__[0] is object:
                raise TypeError(
                    f"'{val.__module__}.{cls_name}' must inherit from 'vedro.Scenario'"
                )

        return False
