from asyncio import gather
from pathlib import Path
from typing import List

from vedro.core import ModuleLoader, Plugin, VirtualScenario

from ._scenario_collector import ScenarioCollector
from ._scenario_provider import ScenarioProvider
from ._scenario_source import ScenarioSource

__all__ = ("MultiProviderCollector",)


class MultiProviderCollector(ScenarioCollector):
    def __init__(self, providers: List[ScenarioProvider], module_loader: ModuleLoader) -> None:
        self._providers = providers
        self._module_loader = module_loader
        if len(providers) == 0:
            raise ValueError("At least one provider must be specified")
        if not all(isinstance(provider, ScenarioProvider) for provider in providers):
            raise TypeError("All providers must be instances of ScenarioProvider")

    async def collect(self, path: Path, *, project_dir: Path) -> List[VirtualScenario]:
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
        if not isinstance(provider, ScenarioProvider):
            raise TypeError("Provider must be an instance of ScenarioProvider")
        self._providers.append(provider)
