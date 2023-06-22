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
        self._fail_after_count: Union[int, None] = None
        self._fail_after_percent: Union[int, None] = None
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
        group = event.arg_parser.add_argument_group("Interrupter")
        exclusive_group = group.add_mutually_exclusive_group()

        # --ff will be removed in v2.0
        exclusive_group.add_argument("--fail-fast", "--ff", "-f",
                                     action="store_true",
                                     default=self._fail_fast,
                                     help="Stop after first failed scenario")
        exclusive_group.add_argument("--fail-after-count", type=int, default=None,
                                     help="Stop after N failed scenarios")
        exclusive_group.add_argument("--fail-after-percent", type=int, default=None,
                                     help="Stop after X%% failed scenarios")

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        self._fail_after_percent = event.args.fail_after_percent
        self._fail_after_count = event.args.fail_after_count
        if event.args.fail_fast:
            self._fail_fast = True
            self._fail_after_count = 1
        elif self._fail_after_count is not None:
            self._fail_fast = True
        elif self._fail_after_percent is not None:
            self._fail_fast = True

    def on_startup(self, event: StartupEvent) -> None:
        if not self._fail_fast:
            return

        if self._fail_after_percent is not None:
            scheduled = len(list(event.scheduler.scheduled))
            self._fail_after_count = max(1, int(scheduled * self._fail_after_percent / 100))

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
        if not self._fail_fast:
            return

        if (self._fail_after_count is not None) and self._failed >= self._fail_after_count:
            raise InterrupterPluginTriggered("Stop after first failed scenario")

    def on_cleanup(self, event: CleanupEvent) -> None:
        if not self._fail_fast:
            return

        for sig, orig_handler in self._orig_handlers.items():
            signal.signal(sig, orig_handler)
        self._orig_handlers = {}


class Interrupter(PluginConfig):
    plugin = InterrupterPlugin
    description = "Stops test execution after the first failed scenario or on specified signals"

    # Raise Interrupted exception on these signals
    handle_signals: Tuple[signal.Signals, ...] = (signal.SIGTERM,)
