from typing import Type

from vedro.core import Dispatcher, Plugin, PluginConfig
from vedro.events import ConfigLoadedEvent

from ._scenario_provider import ScenarioProvider

__all__ = ("Functioner", "FunctionerPlugin",)


class FunctionerPlugin(Plugin):
    def __init__(self, config: Type["Functioner"]) -> None:
        super().__init__(config)

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ConfigLoadedEvent, self.on_config_loaded)

    def on_config_loaded(self, event: ConfigLoadedEvent) -> None:
        scenario_collector = event.config.Registry.ScenarioCollector()
        scenario_collector.register_provider(ScenarioProvider(), self)


class Functioner(PluginConfig):
    plugin = FunctionerPlugin
    description = "Enables a functional-style syntax for defining Vedro scenarios"
