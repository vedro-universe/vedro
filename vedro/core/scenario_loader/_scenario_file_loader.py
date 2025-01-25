import os
from inspect import isclass
from pathlib import Path
from types import ModuleType
from typing import Any, List, Optional, Type

from ..._scenario import Scenario
from ..module_loader import ModuleFileLoader, ModuleLoader
from ._scenario_loader import ScenarioLoader

__all__ = ("ScenarioFileLoader",)


class ScenarioFileLoader(ScenarioLoader):
    """
    Loads scenarios from a file path using a specified module loader.

    This class implements the `ScenarioLoader` interface and provides
    functionality to load scenarios from a given module file path. It uses
    a module loader to load the module and then collects scenarios defined
    within that module.
    """

    def __init__(self, module_loader: Optional[ModuleLoader] = None) -> None:
        """
        Initialize the ScenarioFileLoader with an optional module loader.

        :param module_loader: An optional module loader. If not provided,
                              a default `ModuleFileLoader` is used.
        """
        self._module_loader = module_loader or ModuleFileLoader()  # backward compatibility
        self._enforce_scenario_presence: bool = True  # Add to config in v2

    async def load(self, path: Path) -> List[Type[Scenario]]:
        """
        Load scenarios from the specified path.

        :param path: The path from which to load scenarios.
        :return: A list of loaded scenarios.
        :raises ValueError: If no scenarios are found in the module and
                            `_enforce_scenario_presence` is True.
        """
        module = await self._module_loader.load(path)
        loaded = self._collect_scenarios(module)
        if self._enforce_scenario_presence and len(loaded) == 0:
            raise ValueError(
                f"No Vedro scenarios found in the module at '{path}'. "
                "Ensure the module contains at least one subclass of 'vedro.Scenario'"
            )
        return loaded

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
