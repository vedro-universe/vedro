import json
import sys
from functools import partial
from io import StringIO
from os import linesep
from typing import Callable, Optional, Tuple, Type, Union, final

import vedro
import vedro.plugins.director.rich as rich_reporter
from vedro.core import ConfigType, Dispatcher, PluginConfig, ScenarioScheduler
from vedro.events import (
    CleanupEvent,
    ConfigLoadedEvent,
    ScenarioFailedEvent,
    ScenarioPassedEvent,
    ScenarioReportedEvent,
    ScenarioRunEvent,
    ScenarioSkippedEvent,
    StartupEvent,
)
from vedro.plugins.director import DirectorInitEvent, Reporter
from vedro.plugins.director.rich import make_console

from ._event_types import EventDict
from ._json_formatter import JsonFormatter

__all__ = ("JsonReporter", "JsonReporterPlugin",)

JsonFormatterFactory = Union[
    Type[JsonFormatter],
    Callable[..., JsonFormatter]
]

JsonSerializerFactory = Callable[[EventDict], str]


def pretty_serializer(event: EventDict) -> str:
    return json.dumps(event, indent=2, ensure_ascii=False, separators=(', ', ': '))


def compact_serializer(event: EventDict) -> str:
    return json.dumps(event, ensure_ascii=False, separators=(',', ':'))


@final
class JsonReporterPlugin(Reporter):
    def __init__(self, config: Type["JsonReporter"], *,
                 formatter_factory: JsonFormatterFactory = JsonFormatter,
                 json_serializer: JsonSerializerFactory = pretty_serializer) -> None:
        super().__init__(config)
        self._rich_config = config.RichReporter
        self._formatter_factory = formatter_factory
        self._formatter_inst: Union[JsonFormatter, None] = None
        self._json_serializer = json_serializer
        self._output = sys.stdout
        self._buffer: Union[StringIO, None] = None
        self._global_config: Union[ConfigType, None] = None

    def subscribe(self, dispatcher: Dispatcher) -> None:
        super().subscribe(dispatcher)
        dispatcher.listen(ConfigLoadedEvent, self.on_config_loaded) \
                  .listen(DirectorInitEvent, lambda e: e.director.register("json", self))

    def on_config_loaded(self, event: ConfigLoadedEvent) -> None:
        """
        Handle the event when the configuration is loaded.

        :param event: The ConfigLoadedEvent instance containing the configuration.
        """
        self._global_config = event.config

    def on_chosen(self) -> None:
        assert isinstance(self._dispatcher, Dispatcher)  # for type checking
        assert self._global_config is not None  # for type checking

        if self._rich_config.enabled:
            # Register rich reporter before setting up event listeners
            self._register_rich_reporter()
            self._rich_reporter.on_config_loaded(
                # Rich reporter needs global config to access Registry.TracebackFilter
                ConfigLoadedEvent(self._global_config.path, self._global_config)
            )

        tb_filter_factory = self._global_config.Registry.TracebackFilter
        self._formatter_inst = self._formatter_factory(tb_filter_factory([vedro]))

        self._dispatcher.listen(StartupEvent, self.on_startup) \
            .listen(ScenarioSkippedEvent, self.on_scenario_skipped) \
            .listen(ScenarioRunEvent, self.on_scenario_run) \
            .listen(ScenarioFailedEvent, self.on_scenario_failed) \
            .listen(ScenarioPassedEvent, self.on_scenario_passed) \
            .listen(ScenarioReportedEvent, self.on_scenario_reported) \
            .listen(CleanupEvent, self.on_cleanup)

    @property
    def _formatter(self) -> JsonFormatter:
        assert self._formatter_inst is not None
        return self._formatter_inst

    def _register_rich_reporter(self) -> None:
        assert isinstance(self._dispatcher, Dispatcher)

        self._buffer = StringIO()
        console_factory = partial(make_console, file=self._buffer)
        printer_factory = partial(rich_reporter.RichPrinter, console_factory=console_factory)
        self._rich_reporter = rich_reporter.RichReporterPlugin(self._rich_config,
                                                               printer_factory=printer_factory)

        self._rich_reporter._dispatcher = self._dispatcher
        self._rich_reporter.on_chosen()

    def _calculate_discovery_stats(self, scheduler: ScenarioScheduler) -> Tuple[int, int, int]:
        """
        Calculate discovery statistics from the scheduler.

        :param scheduler: The Scheduler instance containing scenario information.
        :return: A tuple of (discovered, scheduled, skipped) counts.
        """
        discovered = sum(1 for _ in scheduler.discovered)
        scheduled = 0
        skipped = 0
        for scenario in scheduler.scheduled:
            scheduled += 1
            if scenario.is_skipped():
                skipped += 1

        return discovered, scheduled, skipped

    def on_startup(self, event: StartupEvent) -> None:
        discovered, scheduled, skipped = self._calculate_discovery_stats(event.scheduler)

        rich_output = self._consume_rich_output()
        event_data = self._formatter.format_startup_event(discovered, scheduled, skipped,
                                                          rich_output=rich_output)
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
        rich_output = self._consume_rich_output()
        event_data = self._formatter.format_scenario_reported_event(event.aggregated_result,
                                                                    rich_output=rich_output)
        self._emit_event(event_data)

    def on_cleanup(self, event: CleanupEvent) -> None:
        rich_output = self._consume_rich_output()
        event_data = self._formatter.format_cleanup_event(event.report, rich_output=rich_output)
        self._emit_event(event_data)

    def _emit_event(self, event: EventDict) -> None:
        json_event = self._json_serializer(event)
        self._output.write(json_event + linesep)
        self._output.flush()

    def _consume_rich_output(self) -> Optional[str]:
        if self._buffer is None:
            return None
        output = self._buffer.getvalue()
        self._buffer.truncate(0)
        self._buffer.seek(0)
        return output


class JsonReporter(PluginConfig):
    plugin = JsonReporterPlugin
    description = ""

    class RichReporter(rich_reporter.RichReporter):
        enabled = True
        hide_namespaces = True
        show_timings = True
        show_captured_output = True
