from vedro.core import ConfigType, Dispatcher, Plugin, PluginConfig
from vedro.events import ArgParsedEvent, ArgParseEvent, ConfigLoadedEvent

from .random_orderer import RandomOrderer
from .reversed_orderer import ReversedOrderer
from .stable_orderer import StableScenarioOrderer

__all__ = ("Orderer", "OrdererPlugin")


class OrdererPlugin(Plugin):
    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ConfigLoadedEvent, self.on_config_loaded) \
            .listen(ArgParseEvent, self.on_arg_parse) \
            .listen(ArgParsedEvent, self.on_arg_parsed)

    def on_config_loaded(self, event: ConfigLoadedEvent) -> None:
        self._global_config: ConfigType = event.config

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        group = event.arg_parser.add_argument_group("Orderer")
        exgroup = group.add_mutually_exclusive_group()

        exgroup.add_argument("--order-stable", action="store_true", default=True,
                             help="Set stable scenario order (default)")
        exgroup.add_argument("--order-reversed", action="store_true", default=False,
                             help="Set reversed scenario order")
        exgroup.add_argument("--order-random", action="store_true", default=False,
                             help="Set random scenario order")

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        if event.args.order_stable:
            self._global_config.Registry.ScenarioOrderer.register(StableScenarioOrderer, self)

        if event.args.order_reversed:
            self._global_config.Registry.ScenarioOrderer.register(ReversedOrderer, self)

        if event.args.order_random:
            self._global_config.Registry.ScenarioOrderer.register(RandomOrderer, self)


class Orderer(PluginConfig):
    plugin = OrdererPlugin
