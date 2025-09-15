import json
import sys
from functools import partial
from io import StringIO
from os import linesep
from typing import Callable, Optional, TextIO, Tuple, Type, Union, final

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


def compact_serializer(event: EventDict) -> str:
    """
    Serialize an event mapping into a compact JSON string.

    The serializer disables ASCII escaping and uses minimal separators to
    reduce output size while remaining human-inspectable.

    :param event: The event to serialize (minimal fields as defined by ``EventDict``).
    :return: The serialized JSON line representing the event.
    :raises TypeError: If the event contains non-serializable values.
    :raises ValueError: If serialization fails due to malformed data.
    """
    return json.dumps(event, ensure_ascii=False, separators=(',', ':'))


@final
class JsonReporterPlugin(Reporter):
    """
    Provides a Vedro reporter that emits structured JSON events.

    The reporter formats lifecycle events into standardized JSON payloads and
    writes them to a text stream (stdout by default). When the rich reporter is
    enabled, it captures its terminal output and attaches it as ``rich_output``
    to the corresponding JSON events.
    """

    def __init__(self, config: Type["JsonReporter"], *,
                 formatter_factory: JsonFormatterFactory = JsonFormatter,
                 json_serializer: JsonSerializerFactory = compact_serializer,
                 output: Optional[TextIO] = None) -> None:
        """
        Initialize the JSON reporter plugin.

        :param config: The configuration class providing nested settings,
                       including integration with the rich reporter.
        :param formatter_factory: The factory used to create a JSON formatter
                                  instance. Defaults to the built-in formatter.
        :param json_serializer: The function that converts an event mapping to
                                a JSON string. Defaults to a compact serializer.
        :param output: The stream to write JSON lines to. Defaults to
                       ``sys.stdout`` when not provided.
        """
        super().__init__(config)
        self._rich_config = config.RichReporter
        self._formatter_factory = formatter_factory
        self._formatter_inst: Union[JsonFormatter, None] = None
        self._json_serializer = json_serializer
        self._output = output if (output is not None) else sys.stdout
        self._buffer: Union[StringIO, None] = None
        self._global_config: Union[ConfigType, None] = None

    def subscribe(self, dispatcher: Dispatcher) -> None:
        """
        Subscribe the reporter to framework-level events.

        Attach handlers for configuration loading and director initialization.
        If the rich reporter is enabled, register a buffered instance to
        capture its output.

        :param dispatcher: The central dispatcher to listen to.
        """
        super().subscribe(dispatcher)
        dispatcher.listen(ConfigLoadedEvent, self.on_config_loaded) \
                  .listen(DirectorInitEvent, lambda e: e.director.register("json", self))

        if self._rich_config.enabled:
            self._register_rich_reporter(dispatcher)

    def on_config_loaded(self, event: ConfigLoadedEvent) -> None:
        """
        Store the loaded global configuration.

        Persist the configuration for later use when constructing the
        formatter with an appropriate traceback filter.

        :param event: The configuration loaded event with the global config.
        """
        self._global_config = event.config

    def on_chosen(self) -> None:
        """
        Finalize setup when the reporter is selected.

        Create the formatter instance using the configured traceback filter
        and subscribe to runtime lifecycle events for JSON emission.
        """
        assert isinstance(self._dispatcher, Dispatcher)  # for type checking
        assert self._global_config is not None  # for type checking

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
        """
        Return the instantiated JSON formatter.

        :return: The active JSON formatter instance used to build event payloads.
        """
        assert self._formatter_inst is not None  # for type checking
        return self._formatter_inst

    def _register_rich_reporter(self, dispatcher: Dispatcher) -> None:
        """
        Register a buffered rich reporter to capture terminal output.

        Create a memory-backed console to collect rich-rendered text, and
        subscribe the wrapped rich reporter to the same dispatcher.

        :param dispatcher: The central dispatcher to wire the rich reporter into.
        """
        self._buffer = StringIO()
        console_factory = partial(make_console, file=self._buffer)
        printer_factory = partial(rich_reporter.RichPrinter, console_factory=console_factory)
        self._rich_reporter = rich_reporter.RichReporterPlugin(self._rich_config,
                                                               printer_factory=printer_factory)

        self._rich_reporter.subscribe(dispatcher)

    def _calculate_discovery_stats(self, scheduler: ScenarioScheduler) -> Tuple[int, int, int]:
        """
        Compute discovery statistics from the scheduler.

        Iterate discovered and scheduled scenarios to derive counts, including
        how many are marked as skipped.

        :param scheduler: The scheduler holding discovered and scheduled scenarios.
        :return: A ``(discovered, scheduled, skipped)`` tuple of counts.
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
        """
        Emit a startup JSON event with discovery statistics.

        Optionally include any captured rich output produced during startup.

        :param event: The startup event containing the scheduler.
        """
        discovered, scheduled, skipped = self._calculate_discovery_stats(event.scheduler)

        rich_output = self._consume_rich_output()
        event_data = self._formatter.format_startup_event(discovered, scheduled, skipped,
                                                          rich_output=rich_output)
        self._emit_event(event_data)

    def on_scenario_run(self, event: ScenarioRunEvent) -> None:
        """
        Emit a JSON event when a scenario begins execution.

        :param event: The scenario run event with the scenario result.
       """
        event_data = self._formatter.format_scenario_run_event(event.scenario_result)
        self._emit_event(event_data)

    def on_scenario_passed(self, event: ScenarioPassedEvent) -> None:
        """
        Emit a JSON event when a scenario passes.

        :param event: The scenario passed event with the scenario result.
        """
        event_data = self._formatter.format_scenario_passed_event(event.scenario_result)
        self._emit_event(event_data)

    def on_scenario_failed(self, event: ScenarioFailedEvent) -> None:
        """
        Emit a JSON event when a scenario fails.

        :param event: The scenario failed event with the scenario result.
        """
        event_data = self._formatter.format_scenario_failed_event(event.scenario_result)
        self._emit_event(event_data)

    def on_scenario_skipped(self, event: ScenarioSkippedEvent) -> None:
        """
        Emit a JSON event when a scenario is skipped.

        :param event: The scenario skipped event with the scenario result.
        """
        event_data = self._formatter.format_scenario_skipped_event(event.scenario_result)
        self._emit_event(event_data)

    def on_scenario_reported(self, event: ScenarioReportedEvent) -> None:
        """
        Emit a JSON event with the final per-scenario report.

        Optionally include any captured rich output produced during scenario
        execution and reporting.

        :param event: The scenario reported event with aggregated results.
        """
        rich_output = self._consume_rich_output()
        event_data = self._formatter.format_scenario_reported_event(event.aggregated_result,
                                                                    rich_output=rich_output)
        self._emit_event(event_data)

    def on_cleanup(self, event: CleanupEvent) -> None:
        """
        Emit a cleanup JSON event with the aggregate run report.

        Optionally include any captured rich output produced during cleanup.

        :param event: The cleanup event containing the final report.
        """
        rich_output = self._consume_rich_output()
        event_data = self._formatter.format_cleanup_event(event.report, rich_output=rich_output)
        self._emit_event(event_data)

    def _emit_event(self, event: EventDict) -> None:
        """
        Serialize and write a single event as a JSON line.

        The event is serialized via the configured serializer and flushed to the
        output stream to ensure real-time consumption by downstream tools.

        :param event: The event mapping to serialize and write.
        """
        json_event = self._json_serializer(event)
        self._output.write(json_event + linesep)
        self._output.flush()

    def _consume_rich_output(self) -> Optional[str]:
        """
        Retrieve and clear any buffered rich-rendered output.

        If the rich reporter buffer is not configured, return ``None``. When
        present, return the current buffer contents and reset it for reuse.

        :return: The captured rich output text or ``None`` if unavailable.
        """
        if self._buffer is None:
            return None
        output = self._buffer.getvalue()
        self._buffer.truncate(0)
        self._buffer.seek(0)
        return output


class JsonReporter(PluginConfig):
    """
    Declares configuration for the JSON reporter plugin.

    The configuration exposes a nested ``RichReporter`` section to control how
    rich-rendered output integrates with JSON events.
    """

    plugin = JsonReporterPlugin
    description = "Outputs test results as JSON events for machine-readable reporting"

    class RichReporter(rich_reporter.RichReporter):
        """
        Configures the embedded rich reporter used for captured output.

        The settings control whether the rich reporter is enabled, under what
        display name it appears, and visibility of namespaces and captured I/O.
        """
        enabled = True
        reporter_name = "json-rich"
        hide_namespaces = True
        show_captured_output = True
