import sys
from typing import Callable, Type

from vedro.core import Dispatcher, Plugin, PluginConfig
from vedro.events import ArgParsedEvent, ArgParseEvent, CleanupEvent

__all__ = ("Terminator", "TerminatorPlugin",)


class TerminatorPlugin(Plugin):
    def __init__(self, config: Type["Terminator"], *, exit_fn: Callable[[int], None] = sys.exit):
        super().__init__(config)
        self._exit_fn = exit_fn
        self._no_scenarios_ok: bool = False

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ArgParseEvent, self.on_arg_parse) \
                  .listen(ArgParsedEvent, self.on_arg_parsed) \
                  .listen(CleanupEvent, self.on_cleanup, priority=sys.maxsize)

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        event.arg_parser.add_argument("--no-scenarios-ok",
                                      action="store_true",
                                      default=self._no_scenarios_ok,
                                      help="Exit with code 0 even if no scenarios are executed")

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        self._no_scenarios_ok = event.args.no_scenarios_ok

    def on_cleanup(self, event: CleanupEvent) -> None:
        if event.report.interrupted:
            exc = event.report.interrupted.value
            if isinstance(exc, SystemExit) and (exc.code is not None):
                self._exit_fn(int(exc.code))
            else:
                self._exit_fn(130)
        elif event.report.failed > 0:
            self._exit_fn(1)
        elif not self._no_scenarios_ok and event.report.passed == 0:
            self._exit_fn(1)
        else:
            self._exit_fn(0)


class Terminator(PluginConfig):
    plugin = TerminatorPlugin
    description = "Handles exit status based on test results and interruptions"
