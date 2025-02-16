import importlib
import importlib.util
import sys
from importlib.abc import Loader
from importlib.machinery import ModuleSpec
from keyword import iskeyword
from pathlib import Path
from types import ModuleType
from typing import cast

from ._module_loader import ModuleLoader

__all__ = ("ModuleFileLoader",)


class ModuleFileLoader(ModuleLoader):
    """
    Loads a module from a file path with optional validation of module names.

    This class implements the ModuleLoader abstract base class, providing functionality
    to load a module from a specified file path. Optionally, it can validate the module
    names derived from the file paths to ensure they are valid Python identifiers.
    """

    def __init__(self, *, validate_module_names: bool = False) -> None:
        """
        Initialize the ModuleFileLoader with optional module name validation.

        :param validate_module_names: Flag to indicate whether module names should be
                                      validated. Defaults to False.
        """
        self._validate_module_names = validate_module_names
        # Maybe add project root path here in v2

    async def load(self, path: Path) -> ModuleType:
        """
        Load a module from the specified file path.

        :param path: The file path to load the module from.
        :return: The loaded module.
        :raises ValueError: If the module name derived from the path is invalid and
                            validation is enabled.
        :raises ModuleNotFoundError: If the module spec could not be created from the path.
        """
        spec = self._spec_from_path(path)
        module = self._module_from_spec(spec)
        sys.modules[spec.name] = module

        self._exec_module(cast(Loader, spec.loader), module)

        return module

    def _path_to_module_name(self, path: Path) -> str:
        """
        Convert a file path to a module name, optionally validating the name.

        :param path: The file path to convert.
        :return: The derived module name.
        :raises ValueError: If the module name derived from the path is invalid and
                            validation is enabled.
        """
        parts = path.with_suffix("").parts

        # Handle absolute paths by ignoring the root part (e.g., '/' or 'C:\')
        if path.is_absolute():
            parts = parts[1:]

        if self._validate_module_names:
            for part in parts:
                if not self._is_valid_identifier(part):
                    raise ValueError(
                        f"The module name derived from the path '{path}' is invalid "
                        f"due to the segment '{part}'. A valid module name should "
                        "start with a letter or underscore, contain only letters, "
                        "digits, or underscores, and not be a Python keyword."
                    )
        return ".".join(parts)

    def _is_valid_identifier(self, name: str) -> bool:
        """
        Check if a string is a valid Python identifier and not a keyword.

        :param name: The string to check.
        :return: True if the string is a valid identifier, False otherwise.
        """
        return name.isidentifier() and not iskeyword(name)

    def _spec_from_path(self, path: Path) -> ModuleSpec:
        """
        Create a module specification from a file path.

        :param path: The file path to create the spec from.
        :return: The created module specification.
        :raises ModuleNotFoundError: If the module spec could not be created from the path.
        """
        module_name = self._path_to_module_name(path)
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None:
            raise ModuleNotFoundError(module_name)
        return spec

    def _module_from_spec(self, spec: ModuleSpec) -> ModuleType:
        """
        Create a module from a module specification.

        :param spec: The module specification to create the module from.
        :return: The created module.
        """
        return importlib.util.module_from_spec(spec)

    def _exec_module(self, loader: Loader, module: ModuleType) -> None:
        """
        Execute a module using its loader.

        :param loader: The loader to use for executing the module.
        :param module: The module to execute.
        """
        loader.exec_module(module)
