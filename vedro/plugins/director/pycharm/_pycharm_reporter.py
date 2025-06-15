from typing import Any, Callable, Dict, Type, final

from vedro.core import Dispatcher, PluginConfig, ScenarioResult
from vedro.events import (
    ArgParsedEvent,
    ArgParseEvent,
    CleanupEvent,
    ScenarioFailedEvent,
    ScenarioPassedEvent,
    ScenarioRunEvent,
    ScenarioSkippedEvent,
)

from .._director_init_event import DirectorInitEvent
from .._reporter import Reporter
from ..rich import RichPrinter

__all__ = ("PyCharmReporter", "PyCharmReporterPlugin",)


@final
class PyCharmReporterPlugin(Reporter):
    """
    Outputs scenario results in a format compatible with JetBrains TeamCity.

    This reporter integrates with PyCharm to show scenario progress and
    results using TeamCity service messages.
    """

    def __init__(self, config: Type["PyCharmReporter"], *,
                 printer_factory: Callable[[], RichPrinter] = RichPrinter) -> None:
        """
        Initialize the reporter with configuration and printer.

        :param config: Configuration class instance.
        :param printer_factory: Factory to create RichPrinter instances.
        """
        super().__init__(config)
        self._printer = printer_factory()
        self._show_internal_calls = config.show_internal_calls
        self._show_skipped = config.show_skipped
        self._no_output = config.no_output

    def subscribe(self, dispatcher: Dispatcher) -> None:
        """
        Subscribe to the dispatcher and register with the Director.

        :param dispatcher: The event dispatcher instance.
        """
        super().subscribe(dispatcher)
        dispatcher.listen(DirectorInitEvent, lambda e: e.director.register("pycharm", self))

    def on_chosen(self) -> None:
        """
        Register relevant event listeners after reporter is chosen.
        """
        assert isinstance(self._dispatcher, Dispatcher)
        self._dispatcher.listen(ArgParseEvent, self.on_arg_parse) \
                        .listen(ArgParsedEvent, self.on_arg_parsed) \
                        .listen(ScenarioRunEvent, self.on_scenario_run) \
                        .listen(ScenarioPassedEvent, self.on_scenario_passed) \
                        .listen(ScenarioFailedEvent, self.on_scenario_failed) \
                        .listen(ScenarioSkippedEvent, self.on_scenario_skipped) \
                        .listen(CleanupEvent, self.on_cleanup)

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        """
        Define CLI options specific to the PyCharm reporter.

        :param event: The ArgParseEvent during CLI argument parsing.
        """
        group = event.arg_parser.add_argument_group("PyCharm Reporter")
        group.add_argument("--pycharm-no-output", action="store_true",
                           default=self._no_output, help="Don't produce report output")
        group.add_argument("--pycharm-show-skipped", action="store_true",
                           default=self._show_skipped,
                           help="Show skipped scenarios (deprecated, default: True)")
        group.add_argument("--pycharm-show-internal-calls", action="store_true",
                           default=self._show_internal_calls,
                           help="Show internal calls in the traceback output")

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        """
        Apply CLI argument values to internal configuration.

        :param event: The ArgParsedEvent triggered after parsing.
        """
        self._show_internal_calls = event.args.pycharm_show_internal_calls
        self._show_skipped = event.args.pycharm_show_skipped
        self._no_output = event.args.pycharm_no_output

    def on_scenario_run(self, event: ScenarioRunEvent) -> None:
        """
        Output a 'testStarted' message when a scenario begins.

        :param event: The event representing a running scenario.
        """
        scenario_result = event.scenario_result
        location_hint = f"file://{scenario_result.scenario.path}"
        if lineno := scenario_result.scenario.lineno:
            location_hint += f":{lineno}"

        self._write_message("testStarted", {
            "name": scenario_result.scenario.subject,
            "locationHint": location_hint,
        })

    def _print_scenario(self, scenario_result: ScenarioResult) -> None:
        """
        Print scenario information to the console if not disabled.

        :param scenario_result: The result object of the scenario.
        """
        if self._no_output:
            return

        self._printer.print_scenario_subject(scenario_result.scenario.subject,
                                             scenario_result.status, prefix=" ")

        if not scenario_result.is_failed():
            return

        for step_result in scenario_result.step_results:
            self._printer.print_step_name(step_result.step_name, step_result.status,
                                          prefix=" " * 3)
            if step_result.exc_info:
                self._printer.print_exception(step_result.exc_info,
                                              show_internal_calls=self._show_internal_calls)

        if scenario_result.scope:
            self._printer.print_scope(scenario_result.scope)

    def on_scenario_passed(self, event: ScenarioPassedEvent) -> None:
        """
        Output result when a scenario passes.

        :param event: The event triggered after scenario passed.
        """
        scenario_result = event.scenario_result
        self._print_scenario(scenario_result)
        self._write_message("testFinished", {
            "name": scenario_result.scenario.subject,
            "duration": int(scenario_result.elapsed * 1000),
        })

    def on_scenario_failed(self, event: ScenarioFailedEvent) -> None:
        """
        Output result when a scenario fails.

        :param event: The event triggered after scenario failed.
        """
        scenario_result = event.scenario_result
        self._print_scenario(scenario_result)
        self._write_message("testFailed", {
            "name": scenario_result.scenario.subject,
            "message": "",
            "details": "",
        })
        self._write_message("testFinished", {
            "name": scenario_result.scenario.subject,
            "duration": int(scenario_result.elapsed * 1000),
        })

    def on_scenario_skipped(self, event: ScenarioSkippedEvent) -> None:
        """
        Output result when a scenario is skipped, if enabled.

        :param event: The event triggered when a scenario is skipped.
        """
        if not self._show_skipped:
            return
        scenario_result = event.scenario_result
        self._print_scenario(scenario_result)
        self._write_message("testIgnored", {
            "name": scenario_result.scenario.subject,
        })

    def on_cleanup(self, event: CleanupEvent) -> None:
        """
        Handle cleanup and print interruption info if present.

        :param event: The cleanup event after test execution.
        """
        if self._no_output:
            return

        if event.report.interrupted:
            self._printer.print_interrupted(event.report.interrupted)

    def _escape_value(self, value: str) -> str:
        """
        Escape special characters for TeamCity output format.

        :param value: The value to be escaped.
        :return: The escaped string.
        """
        symbols = {"'": "|'", "\n": "|n", "\r": "|r", "|": "||", "[": "|[", "]": "|]"}
        return value.translate({ord(k): v for k, v in symbols.items()})

    def _write_message(self, name: str, attributes: Dict[str, Any]) -> None:
        """
        Write a TeamCity-compatible service message to the console.

        :param name: The message type (e.g., 'testStarted').
        :param attributes: The key-value pairs to include in the message.
        """
        message = f"##teamcity[{name}"
        for key, val in attributes.items():
            escaped = self._escape_value(str(val))
            message += f" {key}='{escaped}'"
        message += "]"
        self._printer.console.out(message)


class PyCharmReporter(PluginConfig):
    """
    Configuration for PyCharmReporterPlugin.

    Defines options for how output is displayed in PyCharm-compatible format.
    """
    plugin = PyCharmReporterPlugin
    description = "Outputs scenario results in a PyCharm-friendly format"

    show_internal_calls: bool = False
    """
   Show internal calls in the traceback output.

   When enabled, traceback output includes frames from the framework's core internals.
   """

    show_skipped: bool = True
    """
    Show skipped scenarios in the output.

    When enabled, skipped scenarios will appear in the test report.
    """

    no_output: bool = False
    """
    Disable all output from the reporter.

    When set to True, no scenario output is printed to the console or IDE.
    TeamCity service messages are still emitted. This option exists for backward compatibility.
    """
