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
    """
    A loader class for loading Python modules from file paths.

    This class extends ModuleLoader to provide functionality for loading modules
    from filesystem paths.
    """

    async def load(self, path: Path) -> ModuleType:
        """
        Load a module from a file path.

        :param path: The file path of the module to be loaded.
        :return: The loaded module.
        """
        spec = self._spec_from_path(path)
        module = self._module_from_spec(spec)
        self._exec_module(cast(Loader, spec.loader), module)
        return module

    def _path_to_module_name(self, path: Path) -> str:
        """
        Convert a file path to a module name.

        :param path: The file path to be converted.
        :return: The corresponding module name.
        """
        return ".".join(path.with_suffix("").parts)

    def _spec_from_path(self, path: Path) -> ModuleSpec:
        """
        Create a module specification from a file path.

        :param path: The file path for which to create the module specification.
        :return: The module specification for the given path.
        :raises ModuleNotFoundError: If no module specification can be created from the path.
        """
        module_name = self._path_to_module_name(path)
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None:
            raise ModuleNotFoundError(module_name)
        return spec

    def _module_from_spec(self, spec: ModuleSpec) -> ModuleType:
        """
        Load a module from a module specification.

        :param spec: The module specification from which to load the module.
        :return: The loaded module.
        """
        return importlib.util.module_from_spec(spec)

    def _exec_module(self, loader: Loader, module: ModuleType) -> None:
        """
        Execute a loaded module.

        :param loader: The loader to use for executing the module.
        :param module: The module to be executed.
        """
        loader.exec_module(module)
