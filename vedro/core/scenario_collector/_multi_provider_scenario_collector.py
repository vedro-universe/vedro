from asyncio import gather
from pathlib import Path
from typing import Callable, List, Union

from .._plugin import Plugin
from .._virtual_scenario import VirtualScenario
from ..module_loader import ModuleLoader
from ._scenario_collector import ScenarioCollector
from ._scenario_provider import ScenarioProvider
from ._scenario_source import ScenarioSource

__all__ = ("MultiProviderScenarioCollector",)


class MultiProviderScenarioCollector(ScenarioCollector):
    """
    Collects scenarios using multiple scenario providers.

    This class aggregates the results of multiple ScenarioProvider instances. It ensures all
    providers are valid and combines their outputs into a single list of VirtualScenario objects.
    """

    def __init__(self, providers: List[ScenarioProvider],
                 module_loader_factory: Callable[[], ModuleLoader]) -> None:
        """
        Initialize MultiProviderScenarioCollector with providers and a module-loader factory.

        :param providers: A sequence of ScenarioProvider instances used to collect scenarios.
        :param module_loader_factory: A callable returning a fresh ModuleLoader when invoked.
        :raises ValueError: If the providers sequence is empty.
        :raises TypeError: If any item in providers is not a ScenarioProvider.
        """
        self._providers = providers
        self._module_loader_factory = module_loader_factory
        if len(providers) == 0:
            raise ValueError("At least one provider must be specified")
        if not all(isinstance(provider, ScenarioProvider) for provider in providers):
            raise TypeError("All providers must be instances of ScenarioProvider")

        self._cached_module_loader: Union[ModuleLoader, None] = None

    @property
    def providers(self) -> List[ScenarioProvider]:
        """
        Get the list of registered scenario providers.

        :return: A list of ScenarioProvider instances.
        """
        return self._providers

    @property
    def _module_loader(self) -> ModuleLoader:
        """
        Return the current ModuleLoader, resolving the factory once and caching
        the result.

        The registry is therefore free to change the registered loader right up
        until the first scenario collection. After that, the loader is frozen to guarantee
        consistency during the run.

        :return: The current ModuleLoader instance.
        """
        if self._cached_module_loader is None:
            self._cached_module_loader = self._module_loader_factory()
        return self._cached_module_loader

    async def collect(self, path: Path, *, project_dir: Path) -> List[VirtualScenario]:
        """
        Collect scenarios from the specified path using all registered providers.

        :param path: The file path to collect scenarios from.
        :param project_dir: The root directory of the project.
        :return: A combined list of VirtualScenario instances from all providers.
        :raises Exception: If any provider raises an exception during collection.
        :raises TypeError: If a provider returns an invalid result or incorrect types.
        """
        source = ScenarioSource(path, project_dir, self._module_loader)
        results = await gather(
            *(provider.provide(source) for provider in self._providers),
            return_exceptions=True
        )

        scenarios = []
        for res in results:
            if isinstance(res, Exception):
                raise res
            if not isinstance(res, list):
                raise TypeError("Provider must return a list of VirtualScenario")
            for scn in res:
                if not isinstance(scn, VirtualScenario):
                    raise TypeError("Each item in the list must be a VirtualScenario")
                scenarios.append(scn)
        return scenarios

    def register_provider(self, provider: ScenarioProvider, registrant: Plugin) -> None:
        """
        Register an additional scenario provider.

        :param provider: The ScenarioProvider to register.
        :param registrant: The Plugin instance registering the provider.
        :raises TypeError: If the provided object is not a ScenarioProvider.
        """
        if not isinstance(provider, ScenarioProvider):
            raise TypeError("Provider must be an instance of ScenarioProvider")
        self._providers.append(provider)
