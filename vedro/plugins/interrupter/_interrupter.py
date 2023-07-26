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
    """
    Exception raised when the `InterrupterPlugin` conditions are met.

    This exception inherits from the `Interrupted` exception and is used
    specifically by the `InterrupterPlugin` when it is triggered. This could be
    due to the occurrence of specific signals that the plugin is set to handle, or
    when the limit of allowed scenario failures is reached during test execution.
    """
    pass


class InterrupterPlugin(Plugin):
    def __init__(self, config: Type["Interrupter"]) -> None:
        super().__init__(config)
        self._fail_fast: bool = False
        self._fail_after_count: Union[int, None] = None
        self._failed_count: int = 0
        self._signals: Tuple[signal.Signals, ...] = config.handle_signals
        self._orig_handlers: Dict[signal.Signals, Any] = {}

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ArgParseEvent, self.on_arg_parse) \
                  .listen(ArgParsedEvent, self.on_arg_parsed) \
                  .listen(StartupEvent, self.on_startup) \
                  .listen(ScenarioRunEvent, self.on_scenario_execute) \
                  .listen(ScenarioSkippedEvent, self.on_scenario_execute) \
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

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        self._fail_fast = event.args.fail_fast
        self._fail_after_count = event.args.fail_after_count

        if (self._fail_after_count is not None) and (self._fail_after_count < 1):
            raise ValueError("InterrupterPlugin: `fail_after_count` must be >= 1")

    def on_startup(self, event: StartupEvent) -> None:
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
            self._failed_count += 1

    def on_scenario_execute(self, event: Union[ScenarioRunEvent, ScenarioSkippedEvent]) -> None:
        if (not self._fail_fast) and (self._fail_after_count is None):
            return

        if self._fail_fast and self._failed_count >= 1:
            raise InterrupterPluginTriggered("Stop after first failed scenario")

        if self._fail_after_count and self._failed_count >= self._fail_after_count:
            raise InterrupterPluginTriggered(
                f"Stop after {self._fail_after_count} failed scenario")

    def on_cleanup(self, event: CleanupEvent) -> None:
        for sig, orig_handler in self._orig_handlers.items():
            signal.signal(sig, orig_handler)
        self._orig_handlers = {}


class Interrupter(PluginConfig):
    plugin = InterrupterPlugin
    description = "Halts test execution after N failed scenarios or on specified signals"

    # Raise Interrupted exception on these signals
    handle_signals: Tuple[signal.Signals, ...] = (signal.SIGTERM,)
