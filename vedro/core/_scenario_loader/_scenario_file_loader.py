import importlib
import importlib.util
import os
from importlib.abc import Loader
from importlib.machinery import ModuleSpec
from inspect import isclass
from keyword import iskeyword
from pathlib import Path
from types import ModuleType
from typing import Any, List, Type, cast

from ..._scenario import Scenario
from ._scenario_loader import ScenarioLoader

__all__ = ("ScenarioFileLoader",)


class ScenarioFileLoader(ScenarioLoader):
    """
    A class responsible for loading Vedro scenarios from a file.
    """

    async def load(self, path: Path) -> List[Type[Scenario]]:
        """
        Asynchronously load Vedro scenarios from a module at the given path.

        :param path: The file path of the module to load scenarios from.
        :return: A list of loaded Vedro scenario classes.
        :raises ValueError: If no valid Vedro scenarios are found in the module.
        """
        spec = self._spec_from_path(path)
        module = self._module_from_spec(spec)
        self._exec_module(cast(Loader, spec.loader), module)

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

    def _path_to_module_name(self, path: Path) -> str:
        """
        Convert a file path to a valid Python module name.

        :param path: The file path to convert.
        :return: A string representing the module name.
        :raises ValueError: If any part of the path is not a valid Python identifier.
        """
        parts = path.with_suffix("").parts
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
        Check if a string is a valid Python identifier.

        :param name: The string to check.
        :return: True if the string is a valid identifier, False otherwise.
        """
        return name.isidentifier() and not iskeyword(name)

    def _spec_from_path(self, path: Path) -> ModuleSpec:
        """
        Create a module specification from a file path.

        :param path: The file path for which to create the module spec.
        :return: The ModuleSpec for the given path.
        :raises ModuleNotFoundError: If no module specification can be created for the path.
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
        Execute a module that has been loaded.

        :param loader: The loader to use for executing the module.
        :param module: The module to execute.
        """
        loader.exec_module(module)

    def _is_vedro_scenario(self, val: Any) -> bool:
        """
        Determine if a given value is a Vedro scenario class.

        :param val: The value to check.
        :return: True if the value is a Vedro scenario class, False otherwise.
        :raises TypeError: If the value has a name suggesting it's a scenario but
            doesn't inherit from 'vedro.Scenario'.
        :raises ValueError: If the value inherits from 'vedro.Scenario' but its
            name doesn't follow the naming convention.
        """
        # First, check if 'val' is a class. Non-class values are not scenarios
        if not isclass(val):
            return False

        cls_name = val.__name__

        # Exclude the foundational 'Scenario' class and 'VedroTemplate',
        # as these are not user-defined scenario classes
        if (val == Scenario) or (cls_name == "VedroTemplate"):
            return False

        # Check if 'val' is a subclass of 'Scenario' for inheritance validation
        is_scenario_subclass = issubclass(val, Scenario)

        # Check if the name of 'val' follows the naming convention for scenarios
        # It should start or end with 'Scenario'
        has_scenario_in_name = cls_name.startswith("Scenario") or cls_name.endswith("Scenario")

        # If 'val' follows both naming convention and is a subclass of 'Scenario',
        # it's a valid scenario
        if has_scenario_in_name and is_scenario_subclass:
            return True

        # If only the naming convention is followed, raise an error indicating inheritance issue
        elif has_scenario_in_name:
            raise TypeError(f"'{val.__module__}.{cls_name}' must inherit from 'vedro.Scenario'")

        # # If only the inheritance is correct, raise an error about incorrect naming convention
        elif is_scenario_subclass:
            raise ValueError(f"'{val.__module__}.{cls_name}' must have a name "
                             "that starts or ends with 'Scenario'")

        # If neither criteria are met, it's not a scenario
        else:
            return False
