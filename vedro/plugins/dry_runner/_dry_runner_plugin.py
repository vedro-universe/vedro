from typing import Tuple, Type

from vedro.core import ConfigType, Dispatcher, Plugin, PluginConfig
from vedro.events import ArgParsedEvent, ArgParseEvent, ConfigLoadedEvent

from ._dry_runner import DryRunner as DryRunnerImpl


class DryRunnerPlugin(Plugin):
    def __init__(self, config: Type["DryRunner"]) -> None:
        super().__init__(config)
        self._dry_run = False
        self._interrupt_exceptions = config.interrupt_exceptions

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ConfigLoadedEvent, self.on_config_loaded) \
                  .listen(ArgParseEvent, self.on_arg_parse) \
                  .listen(ArgParsedEvent, self.on_arg_parsed)

    def on_config_loaded(self, event: ConfigLoadedEvent) -> None:
        self._global_config: ConfigType = event.config

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        group = event.arg_parser.add_argument_group("Dry Runner")
        group.add_argument("--dry-run", action="store_true", default=self._dry_run,
                           help="Run scenarios without executing them")

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        self._dry_run = event.args.dry_run
        if self._dry_run:
            self._global_config.Registry.ScenarioRunner.register(
                resolver=lambda: DryRunnerImpl(self._global_config.Registry.Dispatcher(),
                                               interrupt_exceptions=self._interrupt_exceptions),
                registrant=self
            )


class DryRunner(PluginConfig):
    plugin = DryRunnerPlugin

    # Exceptions that will interrupt scenario execution
    interrupt_exceptions: Tuple[Type[BaseException], ...] = (KeyboardInterrupt, SystemExit,)
