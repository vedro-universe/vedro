import importlib
import importlib.util
from importlib.abc import Loader
from importlib.machinery import ModuleSpec
from pathlib import Path
from types import ModuleType
from typing import cast

from ._module_loader import ModuleLoader

__all__ = ("ModuleFileLoader",)


class ModuleFileLoader(ModuleLoader):
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

    async def load(self, path: Path) -> ModuleType:
        spec = self._spec_from_path(path)
        module = self._module_from_spec(spec)
        self._exec_module(cast(Loader, spec.loader), module)
        return module
