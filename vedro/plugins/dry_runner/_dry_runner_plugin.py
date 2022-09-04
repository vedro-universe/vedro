from vedro.core import ConfigType, Dispatcher, Plugin, PluginConfig
from vedro.events import ArgParsedEvent, ArgParseEvent, ConfigLoadedEvent

from ._dry_runner import DryRunner as DryRunnerImpl


class DryRunnerPlugin(Plugin):
    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ConfigLoadedEvent, self.on_config_loaded) \
                  .listen(ArgParseEvent, self.on_arg_parse) \
                  .listen(ArgParsedEvent, self.on_arg_parsed)

    def on_config_loaded(self, event: ConfigLoadedEvent) -> None:
        self._global_config: ConfigType = event.config

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        event.arg_parser.add_argument("--dry-run", action="store_true", default=False, help="")

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        self._dry_run = event.args.dry_run
        if self._dry_run:
            self._global_config.Registry.ScenarioRunner.register(
                resolver=lambda: DryRunnerImpl(self._global_config.Registry.Dispatcher()),
                registrant=self
            )


class DryRunner(PluginConfig):
    plugin = DryRunnerPlugin
