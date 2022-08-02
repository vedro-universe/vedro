from typing import Type

from vedro.core import Dispatcher, Plugin, PluginConfig
from vedro.events import ArgParsedEvent, ArgParseEvent, ScenarioReportedEvent, ScenarioRunEvent

__all__ = ("Interrupter", "InterrupterPlugin", "Interrupted",)


class Interrupted(Exception):
    pass


class InterrupterPlugin(Plugin):
    def __init__(self, config: Type["Interrupter"]) -> None:
        super().__init__(config)
        self._fail_fast: bool = False
        self._failed: int = 0

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ArgParseEvent, self.on_arg_parse) \
                  .listen(ArgParsedEvent, self.on_arg_parsed) \
                  .listen(ScenarioRunEvent, self.on_scenario_run) \
                  .listen(ScenarioReportedEvent, self.on_scenario_reported)

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        event.arg_parser.add_argument("--fail-fast", "--ff",
                                      action="store_true",
                                      default=self._fail_fast,
                                      help="Stop after first failed scenario")

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        self._fail_fast = event.args.fail_fast

    def on_scenario_reported(self, event: ScenarioReportedEvent) -> None:
        if event.aggregated_result.is_failed():
            self._failed += 1

    def on_scenario_run(self, event: ScenarioRunEvent) -> None:
        if self._fail_fast and self._failed > 0:
            raise Interrupted()


class Interrupter(PluginConfig):
    plugin = InterrupterPlugin
