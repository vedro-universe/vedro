import os
from inspect import isclass
from pathlib import Path
from typing import Any, List, Optional, Type

from ..._scenario import Scenario
from ..module_loader import ModuleFileLoader, ModuleLoader
from ._scenario_loader import ScenarioLoader

__all__ = ("ScenarioFileLoader",)


class ScenarioFileLoader(ScenarioLoader):
    def __init__(self, module_loader: Optional[ModuleLoader] = None) -> None:
        self._module_loader = module_loader or ModuleFileLoader()  # backward compatibility

    async def load(self, path: Path) -> List[Type[Scenario]]:
        module = await self._module_loader.load(path)

        loaded = []
        # Iterate over the module's dictionary because it preserves the order of definitions,
        # which is not guaranteed when using dir(module)
        for name in module.__dict__:
            if name.startswith("_"):
                continue
            val = getattr(module, name)
            if self._is_vedro_scenario(val):
                val.__file__ = os.path.abspath(module.__file__)  # type: ignore
                loaded.append(val)

        if len(loaded) == 0:
            raise ValueError(
                f"No valid Vedro scenarios found in the module at '{path}'. "
                "Ensure the module contains at least one subclass of 'vedro.Scenario'"
            )
        return loaded

    def _is_vedro_scenario(self, val: Any) -> bool:
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
            raise TypeError(f"'{val.__module__}.{cls_name}' must inherit from 'vedro.Scenario'")

        return False
