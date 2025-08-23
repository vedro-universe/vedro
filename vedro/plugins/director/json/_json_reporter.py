import json
import sys
from os import linesep
from typing import Any, Callable, Dict, Type, Union, final

import vedro
from vedro.core import Dispatcher, PluginConfig
from vedro.events import (
    CleanupEvent,
    ScenarioFailedEvent,
    ScenarioPassedEvent,
    ScenarioReportedEvent,
    ScenarioRunEvent,
    ScenarioSkippedEvent,
    StartupEvent,
)
from vedro.plugins.director import DirectorInitEvent, Reporter

from ._json_formatter import JsonFormatter

__all__ = ("JsonReporter", "JsonReporterPlugin",)

from ..rich.utils import TracebackFilter

JsonFormatterType = Union[
    Type[JsonFormatter],
    Callable[..., JsonFormatter]
]


@final
class JsonReporterPlugin(Reporter):
    def __init__(self, config: Type["JsonReporter"], *,
                 formatter_factory: JsonFormatterType = JsonFormatter) -> None:
        super().__init__(config)
        self._output = sys.stdout
        self._formatter = formatter_factory(TracebackFilter(modules=[vedro]))

    def subscribe(self, dispatcher: Dispatcher) -> None:
        super().subscribe(dispatcher)
        dispatcher.listen(DirectorInitEvent, lambda e: e.director.register("json", self))

    def on_chosen(self) -> None:
        assert isinstance(self._dispatcher, Dispatcher)  # for type checking

        self._dispatcher.listen(StartupEvent, self.on_startup) \
                        .listen(ScenarioSkippedEvent, self.on_scenario_skipped) \
                        .listen(ScenarioRunEvent, self.on_scenario_run) \
                        .listen(ScenarioFailedEvent, self.on_scenario_failed) \
                        .listen(ScenarioPassedEvent, self.on_scenario_passed) \
                        .listen(ScenarioReportedEvent, self.on_scenario_reported) \
                        .listen(CleanupEvent, self.on_cleanup)

    def on_startup(self, event: StartupEvent) -> None:
        scheduler = event.scheduler

        discovered = sum(1 for _ in scheduler.discovered)
        scheduled = 0
        skipped = 0
        for scenario in scheduler.scheduled:
            scheduled += 1
            if scenario.is_skipped():
                skipped += 1

        event_data = self._formatter.format_startup_event(discovered, scheduled, skipped)
        self._emit_event(event_data)

    def on_scenario_run(self, event: ScenarioRunEvent) -> None:
        event_data = self._formatter.format_scenario_run_event(event.scenario_result)
        self._emit_event(event_data)

    def on_scenario_passed(self, event: ScenarioPassedEvent) -> None:
        event_data = self._formatter.format_scenario_passed_event(event.scenario_result)
        self._emit_event(event_data)

    def on_scenario_failed(self, event: ScenarioFailedEvent) -> None:
        event_data = self._formatter.format_scenario_failed_event(event.scenario_result)
        self._emit_event(event_data)

    def on_scenario_skipped(self, event: ScenarioSkippedEvent) -> None:
        event_data = self._formatter.format_scenario_skipped_event(event.scenario_result)
        self._emit_event(event_data)

    def on_scenario_reported(self, event: ScenarioReportedEvent) -> None:
        event_data = self._formatter.format_scenario_reported_event(event.aggregated_result)
        self._emit_event(event_data)

    def on_cleanup(self, event: CleanupEvent) -> None:
        event_data = self._formatter.format_cleanup_event(event.report)
        self._emit_event(event_data)

    def _emit_event(self, event: Dict[str, Any]) -> None:
        json_event = json.dumps(event, indent=2, ensure_ascii=False, separators=(', ', ': '))
        self._output.write(json_event + linesep)
        self._output.flush()


class JsonReporter(PluginConfig):
    plugin = JsonReporterPlugin
    description = ""
