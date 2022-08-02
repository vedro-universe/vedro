from typing import Any, Callable, Dict, Type

from vedro.core import Dispatcher, PluginConfig, ScenarioResult
from vedro.events import ArgParsedEvent, ArgParseEvent, ScenarioReportedEvent, ScenarioRunEvent

from .._director_init_event import DirectorInitEvent
from .._reporter import Reporter
from ..rich import RichPrinter

__all__ = ("PyCharmReporter", "PyCharmReporterPlugin",)


class PyCharmReporterPlugin(Reporter):
    def __init__(self, config: Type["PyCharmReporter"], *,
                 printer_factory: Callable[[], RichPrinter] = RichPrinter) -> None:
        super().__init__(config)
        self._printer = printer_factory()
        self._show_internal_calls = config.show_internal_calls
        self._show_skipped = config.show_skipped

    def subscribe(self, dispatcher: Dispatcher) -> None:
        super().subscribe(dispatcher)
        dispatcher.listen(DirectorInitEvent, lambda e: e.director.register("pycharm", self))

    def on_chosen(self) -> None:
        assert isinstance(self._dispatcher, Dispatcher)
        self._dispatcher.listen(ArgParseEvent, self.on_arg_parse) \
                        .listen(ArgParsedEvent, self.on_arg_parsed) \
                        .listen(ScenarioRunEvent, self.on_scenario_run) \
                        .listen(ScenarioReportedEvent, self.on_scenario_reported)

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        group = event.arg_parser.add_argument_group("PyCharm Reporter")

        group.add_argument("--pycharm-show-skipped",
                           action="store_true",
                           default=self._show_skipped,
                           help="Show skipped scenarios")
        group.add_argument("--pycharm-show-internal-calls",
                           action="store_true",
                           default=self._show_internal_calls,
                           help="Show internal calls in the traceback output")

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        self._show_internal_calls = event.args.pycharm_show_internal_calls
        self._show_skipped = event.args.pycharm_show_skipped

    def on_scenario_run(self, event: ScenarioRunEvent) -> None:
        scenario_result = event.scenario_result
        self._write_message("testStarted", {
            "name": scenario_result.scenario.subject,
            "locationHint": scenario_result.scenario.path,
        })

    def on_scenario_reported(self, event: ScenarioReportedEvent) -> None:
        scenario_result = event.aggregated_result
        if scenario_result.is_passed():
            self._print_scenario_passed(scenario_result)
        elif scenario_result.is_failed():
            self._print_scenario_failed(scenario_result)
        elif scenario_result.is_skipped():
            self._print_scenario_skipped(scenario_result)

    def _print_scenario_passed(self, scenario_result: ScenarioResult) -> None:
        self._printer.print_scenario_subject(scenario_result.scenario.subject,
                                             scenario_result.status)
        self._write_message("testFinished", {
            "name": scenario_result.scenario.subject,
            "duration": int(scenario_result.elapsed * 1000),
        })

    def _print_scenario_failed(self, scenario_result: ScenarioResult) -> None:
        self._printer.print_scenario_subject(scenario_result.scenario.subject,
                                             scenario_result.status)

        for step_result in scenario_result.step_results:
            self._printer.print_step_name(step_result.step_name, step_result.status, prefix="  ")
            if step_result.exc_info:
                self._printer.print_exception(step_result.exc_info)

        if scenario_result.scope:
            self._printer.print_scope(scenario_result.scope)

        self._write_message("testFailed", {
            "name": scenario_result.scenario.subject,
            "message": "",
            "details": "",
        })
        self._write_message("testFinished", {
            "name": scenario_result.scenario.subject,
            "duration": int(scenario_result.elapsed * 1000),
        })

    def _print_scenario_skipped(self, scenario_result: ScenarioResult) -> None:
        if self._show_skipped:
            self._printer.print_scenario_subject(scenario_result.scenario.subject,
                                                 scenario_result.status)
            self._write_message("testIgnored", {
                "name": scenario_result.scenario.subject,
            })

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

    # Show internal calls in the traceback output
    show_internal_calls: bool = False

    # Show skipped scenarios
    show_skipped: bool = True
