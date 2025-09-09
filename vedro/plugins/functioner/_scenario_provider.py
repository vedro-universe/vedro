import inspect
import os
from functools import WRAPPER_ASSIGNMENTS, wraps
from inspect import iscoroutinefunction
from types import ModuleType
from typing import Any, Dict, List, Tuple, Type, cast

from vedro._scenario import Scenario
from vedro.core import VirtualScenario
from vedro.core.scenario_collector import ScenarioProvider, ScenarioSource
from vedro.core.scenario_discoverer import create_vscenario

from ._scenario_descriptor import ScenarioDescriptor

__all__ = ("FuncBasedScenarioProvider",)


class FuncBasedScenarioProvider(ScenarioProvider):
    """
    Provides scenario classes by extracting and building them from a given module source.

    This class extends the base ScenarioProvider to support extraction of scenarios defined using
    ScenarioDescriptor and converts them into instances of VirtualScenario. It handles both
    parameterized and non-parameterized scenarios, applying decorators and assembling
    scenario classes.
    """

    async def provide(self, source: ScenarioSource) -> List[VirtualScenario]:
        """
        Extract and return all VirtualScenario instances from the given source.

        :param source: The scenario source containing a module and project directory information.
        :return: A list of VirtualScenario instances built from the discovered scenarios.
        """
        if source.path.suffix != ".py":
            return []
        module = await source.get_module()
        scenarios = self._collect_scenarios(module)
        return [create_vscenario(scn, project_dir=source.project_dir) for scn in scenarios]

    def _collect_scenarios(self, module: ModuleType) -> List[Type[Scenario]]:
        """
        Collect all scenario classes from the specified module.

        :param module: The module from which to collect scenario descriptors.
        :return: A list of Scenario classes built from descriptors found in the module.
        """
        loaded = []
        for name, val in module.__dict__.items():
            if isinstance(val, ScenarioDescriptor):
                if not name.startswith("_"):
                    scenarios = self._build_vedro_scenarios(val, module)
                    loaded.extend(scenarios)
        return loaded

    def _build_vedro_scenarios(self, descriptor: ScenarioDescriptor,
                               module: ModuleType) -> List[Type[Scenario]]:
        """
        Build one or more Scenario classes from a given descriptor.

        :param descriptor: The descriptor containing scenario definition and metadata.
        :param module: The module in which the scenario is defined.
        :return: A list of Scenario classes, one for each parameterization if applicable.
        """
        if len(descriptor.cases) == 0:
            scenario_cls = self._build_vedro_scenario(descriptor, module)
            return [scenario_cls]

        scenario_cls = self._build_vedro_scenario_with_cases(descriptor, module)

        scenarios = []
        for idx, _ in enumerate(descriptor.cases, start=1):
            scn_name = f"{self._create_scenario_name(descriptor)}_{idx}_VedroScenario"
            scenarios.append(
                # This is a temporary and dirty workaround; to be revisited after the v2 release
                # Logic adapted from the `_Meta` class in vedro/_scenario.py
                cast(Type[Scenario], scenario_cls.__init__.__globals__[scn_name])
            )
        return scenarios

    def _build_vedro_scenario(self, descriptor: ScenarioDescriptor,
                              module: ModuleType) -> Type[Scenario]:
        """
        Build a single Scenario class from a descriptor without parameters.

        :param descriptor: The descriptor defining the scenario behavior and metadata.
        :param module: The module in which the scenario resides.
        :return: A Scenario class derived from the base Scenario.
        """
        attrs = self._build_common_attrs(descriptor, module)
        attrs.update({
            "do": self._make_do(descriptor.fn)
        })
        scenario_cls = type(self._create_scenario_name(descriptor), (Scenario,), attrs)

        for decorator in descriptor.decorators:
            scenario_cls = decorator(scenario_cls)
        return scenario_cls

    def _build_vedro_scenario_with_cases(self, descriptor: ScenarioDescriptor,
                                         module: ModuleType) -> Type[Scenario]:
        """
        Build a Scenario class that supports parameterization.

        :param descriptor: The descriptor containing parameterized test data and metadata.
        :param module: The module where the scenario is defined.
        :return: A Scenario class with parameterized initialization.
        """
        sig = inspect.signature(descriptor.fn)
        param_names = list(sig.parameters.keys())

        def __init__(self, *args: Any, **kwargs: Any) -> None:  # type: ignore
            # Bind the arguments to parameter names
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Store each parameter as a named attribute
            for param_name, value in bound_args.arguments.items():
                setattr(self, param_name, value)

        for params in reversed(descriptor.cases):
            __init__ = params(__init__)

        if iscoroutinefunction(descriptor.fn):
            @wraps(descriptor.fn, assigned=self._get_wrapper_assignments())
            async def do(self, *args: Any, **kwargs: Any):  # type: ignore
                params_kwargs = {name: getattr(self, name) for name in param_names}
                # Merge params_kwargs with provided kwargs, with provided kwargs taking precedence
                merged_kwargs = {**params_kwargs, **kwargs}
                return await descriptor.fn(*args, **merged_kwargs)
        else:
            @wraps(descriptor.fn, assigned=self._get_wrapper_assignments())
            def do(self, *args: Any, **kwargs: Any):  # type: ignore
                params_kwargs = {name: getattr(self, name) for name in param_names}
                # Merge params_kwargs with provided kwargs, with provided kwargs taking precedence
                merged_kwargs = {**params_kwargs, **kwargs}
                return descriptor.fn(*args, **merged_kwargs)

        attrs = self._build_common_attrs(descriptor, module)
        attrs.update({
            "__init__": __init__,
            "do": do,
        })
        scenario_cls = type(self._create_scenario_name(descriptor), (Scenario,), attrs)

        for decorator in descriptor.decorators:
            scenario_cls = decorator(scenario_cls)
        return scenario_cls

    def _build_common_attrs(self, descriptor: ScenarioDescriptor,
                            module: ModuleType) -> Dict[str, Any]:
        """
        Build common attributes for a Scenario class based on the descriptor and module.

        :param descriptor: The descriptor containing scenario metadata and function.
        :param module: The module from which the scenario is defined.
        :return: A dictionary of attributes to be used in the Scenario class.
        """
        return {
            "__module__": module.__name__,
            "__file__": self._create_module_path(module),
            "__lineno__": descriptor.lineno,
            "__doc__": descriptor.fn.__doc__,
            "subject": self._create_subject(descriptor),
            "tags": descriptor.tags,
        }

    def _create_scenario_name(self, descriptor: ScenarioDescriptor) -> str:
        """
        Create a scenario class name based on the descriptor name.

        :param descriptor: The scenario descriptor to derive the name from.
        :return: A string representing the scenario class name.
        """
        return f"{descriptor.name}"

    def _create_subject(self, descriptor: ScenarioDescriptor) -> str:
        """
        Generate the subject string used in the scenario based on the descriptor.

        If the descriptor has a custom subject, use it. Otherwise, generate from the function name.

        :param descriptor: The descriptor containing the scenario metadata.
        :return: A human-readable string subject for the scenario.
        """
        if descriptor.subject is not None:
            return descriptor.subject
        return descriptor.name.replace("_", " ")

    def _create_module_path(self, module: ModuleType) -> str:
        """
        Determine the absolute file path of the given module.

        :param module: The module to retrieve the file path from.
        :return: An absolute path to the module's file.
        """
        return os.path.abspath(str(module.__file__))

    def _make_do(self, fn: Any) -> Any:
        """
        Wrap the given function into a 'do' method for a scenario.

        :param fn: The function to be executed in the scenario.
        :return: A method suitable for the 'do' attribute of a scenario class.
        """
        if iscoroutinefunction(fn):
            @wraps(fn, assigned=self._get_wrapper_assignments())
            async def do(self, *args: Any, **kwargs: Any):  # type: ignore
                return await fn(*args, **kwargs)

            return do
        else:
            @wraps(fn, assigned=self._get_wrapper_assignments())
            def do(self, *args: Any, **kwargs: Any):  # type: ignore
                return fn(*args, **kwargs)

            return do

    def _get_wrapper_assignments(self) -> Tuple[str, ...]:
        return tuple(x for x in WRAPPER_ASSIGNMENTS if x != '__name__')
