from typing import Type

from vedro.core import Dispatcher, Plugin, PluginConfig
from vedro.events import ConfigLoadedEvent

from ._func_based_scenario_provider import FuncBasedScenarioProvider

__all__ = ("Functioner", "FunctionerPlugin",)


class FunctionerPlugin(Plugin):
    """
    Enables functional-style scenario registration within Vedro.

    This plugin integrates with the Vedro plugin system and registers a custom
    scenario provider that supports scenarios defined via functional syntax.
    """

    def __init__(self, config: Type["Functioner"]) -> None:
        """
        Initialize the FunctionerPlugin with the given configuration.

        :param config: The configuration class associated with this plugin.
        """
        super().__init__(config)

    def subscribe(self, dispatcher: Dispatcher) -> None:
        """
        Subscribe to relevant Vedro events.

        :param dispatcher: The dispatcher used to register event listeners.
        """
        dispatcher.listen(ConfigLoadedEvent, self.on_config_loaded)

    def on_config_loaded(self, event: ConfigLoadedEvent) -> None:
        """
        Register the custom ScenarioProvider after the configuration is loaded.

        :param event: The event containing the loaded configuration.
        """
        scenario_collector = event.config.Registry.ScenarioCollector()
        scenario_collector.register_provider(FuncBasedScenarioProvider(), self)


class Functioner(PluginConfig):
    """
    Configuration for the FunctionerPlugin.

    This config enables a functional-style syntax for defining scenarios in Vedro.
    """
    plugin = FunctionerPlugin
    description = "Enables a functional-style syntax for defining Vedro scenarios"
