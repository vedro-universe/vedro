import importlib
import importlib.util
import inspect
import os
from pathlib import Path
from typing import List, Type, cast

from ..._scenario import Scenario
from ._scenario_loader import ScenarioLoader

__all__ = ("ScenarioFileLoader",)


class ScenarioFileLoader(ScenarioLoader):
    def _path_to_module_name(self, path: Path) -> str:
        return ".".join(path.with_suffix("").parts)

    async def load(self, path: Path) -> List[Type[Scenario]]:
        module_name = self._path_to_module_name(path)

        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None:
            # ImportError?
            raise Exception(path)
        module = importlib.util.module_from_spec(spec)

        cast(importlib.abc.Loader, spec.loader).exec_module(module)

        loaded = []
        for name in dir(module):
            val = getattr(module, name)
            if inspect.isclass(val) and issubclass(val, Scenario):
                if not val.__name__.startswith("Scenario"):
                    continue
                val.__file__ = os.path.abspath(module.__file__)
                loaded.append(val)
        return loaded
