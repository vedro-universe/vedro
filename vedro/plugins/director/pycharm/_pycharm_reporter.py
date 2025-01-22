from typing import Any, Callable, Dict, Type, final

from niltype import Nil
from rich.pretty import pretty_repr

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
    def __init__(self, config: Type["PyCharmReporter"], *,
                 printer_factory: Callable[[], RichPrinter] = RichPrinter) -> None:
        super().__init__(config)
        self._printer = printer_factory()
        self._show_internal_calls = config.show_internal_calls
        self._show_skipped = config.show_skipped
        self._no_output = config.no_output
        self._show_comparison = config.show_comparison

    def subscribe(self, dispatcher: Dispatcher) -> None:
        super().subscribe(dispatcher)
        dispatcher.listen(DirectorInitEvent, lambda e: e.director.register("pycharm", self))

    def on_chosen(self) -> None:
        assert isinstance(self._dispatcher, Dispatcher)
        self._dispatcher.listen(ArgParseEvent, self.on_arg_parse) \
                        .listen(ArgParsedEvent, self.on_arg_parsed) \
                        .listen(ScenarioRunEvent, self.on_scenario_run) \
                        .listen(ScenarioPassedEvent, self.on_scenario_passed) \
                        .listen(ScenarioFailedEvent, self.on_scenario_failed) \
                        .listen(ScenarioSkippedEvent, self.on_scenario_skipped) \
                        .listen(CleanupEvent, self.on_cleanup)

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        group = event.arg_parser.add_argument_group("PyCharm Reporter")

        group.add_argument("--pycharm-no-output",
                           action="store_true",
                           default=self._no_output,
                           help="Don't produce report output")
        group.add_argument("--pycharm-show-skipped",
                           action="store_true",
                           default=self._show_skipped,
                           help="Show skipped scenarios (deprecated, default: True)")
        group.add_argument("--pycharm-show-internal-calls",
                           action="store_true",
                           default=self._show_internal_calls,
                           help="Show internal calls in the traceback output")

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        self._show_internal_calls = event.args.pycharm_show_internal_calls
        self._show_skipped = event.args.pycharm_show_skipped
        self._no_output = event.args.pycharm_no_output

    def on_scenario_run(self, event: ScenarioRunEvent) -> None:
        scenario_result = event.scenario_result
        self._write_message("testStarted", {
            "name": scenario_result.scenario.subject,
            "locationHint": scenario_result.scenario.path,
        })

    def _print_scenario(self, scenario_result: ScenarioResult) -> None:
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
        scenario_result = event.scenario_result
        self._print_scenario(scenario_result)
        self._write_message("testFinished", {
            "name": scenario_result.scenario.subject,
            "duration": int(scenario_result.elapsed * 1000),
        })

    def on_scenario_failed(self, event: ScenarioFailedEvent) -> None:
        scenario_result = event.scenario_result

        self._print_scenario(scenario_result)

        comparison_attrs = self._get_comparison_attrs(scenario_result)
        self._write_message("testFailed", {
            "name": scenario_result.scenario.subject,
            "message": "",
            "details": "",
            **comparison_attrs,
        })

        self._write_message("testFinished", {
            "name": scenario_result.scenario.subject,
            "duration": int(scenario_result.elapsed * 1000),
        })

    def _get_comparison_attrs(self, scenario_result: ScenarioResult) -> Dict[str, Any]:
        if not self._show_comparison:
            return {}

        for step_result in scenario_result.step_results:
            if step_result.exc_info is None:
                continue

            exc_value = step_result.exc_info.value
            operator = getattr(exc_value, "__vedro_assert_operator__", Nil)
            if (operator is Nil) or (operator != "=="):
                continue

            actual = getattr(exc_value, "__vedro_assert_left__", Nil)
            expected = getattr(exc_value, "__vedro_assert_right__", Nil)
            if (actual is not Nil) and (expected is not Nil):
                return {
                    "message": "assert actual == expected",
                    "actual": pretty_repr(actual),
                    "expected": pretty_repr(expected),
                    "type": "comparisonFailure",
                }

        return {}

    def on_scenario_skipped(self, event: ScenarioSkippedEvent) -> None:
        if not self._show_skipped:
            return
        scenario_result = event.scenario_result
        self._print_scenario(scenario_result)
        self._write_message("testIgnored", {
            "name": scenario_result.scenario.subject,
        })

    def on_cleanup(self, event: CleanupEvent) -> None:
        if self._no_output:
            return

        if event.report.interrupted:
            self._printer.print_interrupted(event.report.interrupted)

    def _escape_value(self, value: str) -> str:
        symbols = {"'": "|'", "\n": "|n", "\r": "|r", "|": "||", "[": "|[", "]": "|]"}
        return value.translate({ord(k): v for k, v in symbols.items()})

    def _write_message(self, name: str, attributes: Dict[str, Any]) -> None:
        message = f"##teamcity[{name}"
        for key, val in attributes.items():
            escaped = self._escape_value(str(val))
            message += f" {key}='{escaped}'"
        message += "]"
        self._printer.console.out(message)


class PyCharmReporter(PluginConfig):
    plugin = PyCharmReporterPlugin
    description = "Outputs scenario results in a PyCharm-friendly format"

    # Show internal calls in the traceback output
    show_internal_calls: bool = False

    # Show skipped scenarios
    show_skipped: bool = True

    # Don't produce report output
    no_output: bool = False

    # Enable adding expected vs actual comparison to PyCharm messages
    show_comparison: bool = True
