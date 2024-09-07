from typing import final

from vedro.core import ConfigType, Dispatcher, Plugin, PluginConfig
from vedro.core.scenario_orderer import StableScenarioOrderer
from vedro.events import ArgParsedEvent, ArgParseEvent, ConfigLoadedEvent

from .random_orderer import RandomOrderer
from .reversed_orderer import ReversedOrderer

__all__ = ("Orderer", "OrdererPlugin")


@final
class OrdererPlugin(Plugin):
    """
    Plugin to configure the order in which scenarios are executed.

    The `OrdererPlugin` allows users to choose between stable, reversed, or random
    order of scenario execution via command-line arguments. The plugin listens
    to argument parsing events and updates the scenario orderer registry accordingly.
    """

    def subscribe(self, dispatcher: Dispatcher) -> None:
        """
        Subscribe to Vedro events for configuring scenario order.

        :param dispatcher: The dispatcher that listens to events.
        """
        dispatcher.listen(ConfigLoadedEvent, self.on_config_loaded) \
                  .listen(ArgParseEvent, self.on_arg_parse) \
                  .listen(ArgParsedEvent, self.on_arg_parsed)

    def on_config_loaded(self, event: ConfigLoadedEvent) -> None:
        """
        Handle the event when the configuration is loaded.

        Stores the global configuration to be used later for registering the scenario orderer.

        :param event: The ConfigLoadedEvent instance containing the loaded configuration.
        """
        self._global_config: ConfigType = event.config

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        """
        Add command-line arguments for selecting the scenario order.

        Provides mutually exclusive options for choosing between stable, reversed, and random
        scenario order during test execution.

        :param event: The ArgParseEvent instance used for adding arguments.
        """
        group = event.arg_parser.add_argument_group("Orderer")
        exgroup = group.add_mutually_exclusive_group()

        exgroup.add_argument("--order-stable", action="store_true", default=False,
                             help="Set stable scenario order (default)")
        exgroup.add_argument("--order-reversed", action="store_true", default=False,
                             help="Set reversed scenario order")
        exgroup.add_argument("--order-random", action="store_true", default=False,
                             help="Set random scenario order")

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        """
        Handle the event after arguments have been parsed and register the scenario orderer.

        Depending on the argument provided, this method registers either the `RandomOrderer`,
        `ReversedOrderer`, or `StableScenarioOrderer` to the global configuration's scenario
        orderer registry.

        :param event: The ArgParsedEvent instance containing parsed arguments.
        """
        if event.args.order_random:
            self._global_config.Registry.ScenarioOrderer.register(RandomOrderer, self)
            return

        if event.args.order_reversed:
            self._global_config.Registry.ScenarioOrderer.register(ReversedOrderer, self)
            return

        if event.args.order_stable:
            self._global_config.Registry.ScenarioOrderer.register(StableScenarioOrderer, self)


class Orderer(PluginConfig):
    """
    Configuration class for the OrdererPlugin.

    This class provides settings for configuring the order in which scenarios are executed.
    Users can choose between stable (default), reversed, or random order for scenario execution.
    """

    plugin = OrdererPlugin
    description = "Configures the execution order of scenarios"
