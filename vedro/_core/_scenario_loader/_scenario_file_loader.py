import importlib
import importlib.util
import inspect
import os
from importlib.abc import Loader
from importlib.machinery import ModuleSpec
from pathlib import Path
from types import ModuleType
from typing import List, Type, cast

from ..._scenario import Scenario
from ._scenario_loader import ScenarioLoader

__all__ = ("ScenarioFileLoader",)


class ScenarioFileLoader(ScenarioLoader):
    def _path_to_module_name(self, path: Path) -> str:
        return ".".join(path.with_suffix("").parts)

    def _spec_from_path(self, path: Path) -> ModuleSpec:
        module_name = self._path_to_module_name(path)
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None:
            raise ModuleNotFoundError(module_name)
        return spec

    def _module_from_spec(self, spec: ModuleSpec) -> ModuleType:
        return importlib.util.module_from_spec(spec)

    def _exec_module(self, loader: Loader, module: ModuleType) -> None:
        loader.exec_module(module)

    async def load(self, path: Path) -> List[Type[Scenario]]:
        spec = self._spec_from_path(path)
        module = self._module_from_spec(spec)
        self._exec_module(cast(Loader, spec.loader), module)

        loaded = []
        for name in dir(module):
            val = getattr(module, name)
            if inspect.isclass(val) and issubclass(val, Scenario):
                if not val.__name__.startswith("Scenario"):
                    continue
                val.__file__ = os.path.abspath(module.__file__)
                loaded.append(val)
        return loaded
