import signal
from types import FrameType
from typing import Any, Dict, Optional, Tuple, Type, Union

from vedro.core import Dispatcher, Plugin, PluginConfig
from vedro.core.scenario_runner import Interrupted
from vedro.events import (
    ArgParsedEvent,
    ArgParseEvent,
    CleanupEvent,
    ScenarioReportedEvent,
    ScenarioRunEvent,
    ScenarioSkippedEvent,
    StartupEvent,
)

__all__ = ("Interrupter", "InterrupterPlugin", "InterrupterPluginTriggered",)


class InterrupterPluginTriggered(Interrupted):
    pass


class InterrupterPlugin(Plugin):
    def __init__(self, config: Type["Interrupter"]) -> None:
        super().__init__(config)
        self._fail_fast: bool = False
        self._failed: int = 0
        self._signals: Tuple[signal.Signals, ...] = config.handle_signals
        self._orig_handlers: Dict[signal.Signals, Any] = {}

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ArgParseEvent, self.on_arg_parse) \
                  .listen(ArgParsedEvent, self.on_arg_parsed) \
                  .listen(StartupEvent, self.on_startup) \
                  .listen(ScenarioRunEvent, self.on_scenario_run) \
                  .listen(ScenarioSkippedEvent, self.on_scenario_run) \
                  .listen(ScenarioReportedEvent, self.on_scenario_reported) \
                  .listen(CleanupEvent, self.on_cleanup)

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        event.arg_parser.add_argument("--fail-fast", "--ff", "-f",
                                      action="store_true",
                                      default=self._fail_fast,
                                      help="Stop after first failed scenario")

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        self._fail_fast = event.args.fail_fast

    def on_startup(self, event: StartupEvent) -> None:
        if not self._fail_fast:
            return

        def handler(signum: int, frame: Optional[FrameType]) -> None:
            try:
                signame = signal.Signals(signum)
            except ValueError:
                signame = signum  # type: ignore
            raise InterrupterPluginTriggered(f"Stop after signal {signame!r} received")

        for sig in self._signals:
            self._orig_handlers[sig] = signal.getsignal(sig)
            signal.signal(sig, handler)

    def on_scenario_reported(self, event: ScenarioReportedEvent) -> None:
        if event.aggregated_result.is_failed():
            self._failed += 1

    def on_scenario_run(self, event: Union[ScenarioRunEvent, ScenarioSkippedEvent]) -> None:
        if self._fail_fast and self._failed > 0:
            raise InterrupterPluginTriggered("Stop after first failed scenario")

    def on_cleanup(self, event: CleanupEvent) -> None:
        if not self._fail_fast:
            return

        for sig, orig_handler in self._orig_handlers.items():
            signal.signal(sig, orig_handler)
        self._orig_handlers = {}


class Interrupter(PluginConfig):
    plugin = InterrupterPlugin

    # Raise Interrupted exception on these signals
    handle_signals: Tuple[signal.Signals, ...] = (signal.SIGTERM,)
