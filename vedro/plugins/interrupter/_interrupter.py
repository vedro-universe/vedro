from vedro.core import Dispatcher, Plugin
from vedro.events import ArgParsedEvent, ArgParseEvent, ScenarioFailedEvent, ScenarioRunEvent

__all__ = ("Interrupter",)


class _Interrupted(Exception):
    pass


class Interrupter(Plugin):
    def __init__(self) -> None:
        self._fail_fast: bool = False
        self._failed: int = 0

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ArgParseEvent, self.on_arg_parse) \
                  .listen(ArgParsedEvent, self.on_arg_parsed) \
                  .listen(ScenarioRunEvent, self.on_scenario_run) \
                  .listen(ScenarioFailedEvent, self.on_scenario_failed)

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        event.arg_parser.add_argument("--fail-fast",
                                      action='store_true',
                                      default=self._fail_fast,
                                      help="Stop after first failed scenario")

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        self._fail_fast = event.args.fail_fast

    def on_scenario_run(self, event: ScenarioRunEvent) -> None:
        if self._fail_fast and self._failed > 0:
            raise _Interrupted()

    def on_scenario_failed(self, event: ScenarioFailedEvent) -> None:
        if self._fail_fast:
            self._failed += 1
