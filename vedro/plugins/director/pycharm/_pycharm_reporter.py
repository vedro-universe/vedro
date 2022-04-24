import json
import os
from traceback import format_exception
from types import TracebackType
from typing import Any, Callable, Dict, Generator, Tuple, Type

from rich.console import Console
from rich.style import Style

import vedro
from vedro.core import Dispatcher, PluginConfig, ScenarioResult
from vedro.events import (
    ArgParsedEvent,
    ArgParseEvent,
    CleanupEvent,
    ScenarioFailedEvent,
    ScenarioPassedEvent,
    ScenarioRunEvent,
    ScenarioSkippedEvent,
    StartupEvent,
)

from .._director_init_event import DirectorInitEvent
from .._reporter import Reporter
from ..rich.utils import make_console

__all__ = ("PyCharmReporter", "PyCharmReporterPlugin",)


class PyCharmReporterPlugin(Reporter):
    def __init__(self, config: Type["PyCharmReporter"], *,
                 console_factory: Callable[[], Console] = make_console) -> None:
        super().__init__(config)
        self._console = console_factory()
        self._show_internal_calls = config.show_internal_calls
        self._show_skipped = config.show_skipped

    def subscribe(self, dispatcher: Dispatcher) -> None:
        super().subscribe(dispatcher)
        dispatcher.listen(DirectorInitEvent, lambda e: e.director.register("pycharm", self))

    def on_chosen(self) -> None:
        assert isinstance(self._dispatcher, Dispatcher)
        self._dispatcher.listen(ArgParseEvent, self.on_arg_parse) \
                        .listen(ArgParsedEvent, self.on_arg_parsed) \
                        .listen(StartupEvent, self.on_startup) \
                        .listen(ScenarioRunEvent, self.on_scenario_run) \
                        .listen(ScenarioPassedEvent, self.on_scenario_passed) \
                        .listen(ScenarioFailedEvent, self.on_scenario_failed) \
                        .listen(ScenarioSkippedEvent, self.on_scenario_skipped) \
                        .listen(CleanupEvent, self.on_cleanup)

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

    def on_startup(self, event: StartupEvent) -> None:
        self._console.out("Scenarios")

    def on_scenario_run(self, event: ScenarioRunEvent) -> None:
        scenario_result: ScenarioResult = event.scenario_result
        self._write_message("testStarted", {
            "name": scenario_result.scenario.subject,
            "locationHint": scenario_result.scenario.path,
        })

    def on_scenario_passed(self, event: ScenarioPassedEvent) -> None:
        scenario_result: ScenarioResult = event.scenario_result

        subject = f"✔ {scenario_result.scenario.subject}"
        self._console.out(subject, style=Style(color="green"))

        self._write_message("testFinished", {
            "name": scenario_result.scenario.subject,
            "duration": int(scenario_result.elapsed * 1000),
        })

    def on_scenario_failed(self, event: ScenarioFailedEvent) -> None:
        scenario_result: ScenarioResult = event.scenario_result

        subject = f"✗ {scenario_result.scenario.subject}"
        self._console.out(subject, style=Style(color="red"))

        for step_result in scenario_result.step_results:
            if step_result.exc_info:
                self._print_exception(step_result.exc_info.value, step_result.exc_info.traceback)

        if scenario_result.scope:
            self._print_scope(scenario_result.scope)

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
        scenario_result: ScenarioResult = event.scenario_result
        if self._show_skipped:
            self._write_message("testIgnored", {
                "name": scenario_result.scenario.subject,
            })

    def on_cleanup(self, event: CleanupEvent) -> None:
        pass

    def _print_exception(self, exception: BaseException, traceback: TracebackType) -> None:
        if not self._show_internal_calls:
            root = os.path.dirname(vedro.__file__)
            while traceback.tb_next is not None:
                filename = os.path.abspath(traceback.tb_frame.f_code.co_filename)
                if os.path.commonpath([root, filename]) != root:
                    break
                traceback = traceback.tb_next

        formatted = format_exception(type(exception), exception, traceback)
        self._console.out("".join(formatted), style=Style(color="yellow"))

    def _print_scope(self, scope: Dict[Any, Any]) -> None:
        self._console.out("Scope:", style=Style(color="blue", bold=True))
        for key, val in self._format_scope(scope):
            self._console.out(f" {key}: ", end="", style=Style(color="blue"))
            self._console.out(val)

    def _format_scope(self, scope: Dict[Any, Any]) -> Generator[Tuple[str, str], None, None]:
        for key, val in scope.items():
            try:
                val_repr = json.dumps(val, ensure_ascii=False, indent=4)
            except:  # noqa: E722
                val_repr = repr(val)
            yield str(key), val_repr

    def _escape_value(self, value: str) -> str:
        symbols = {"'": "|'", "\n": "|n", "\r": "|r", "|": "||", "[": "|[", "]": "|]"}
        return value.translate({ord(k): v for k, v in symbols.items()})

    def _write_message(self, name: str, attributes: Dict[str, Any]) -> None:
        message = f"##teamcity[{name}"
        for key, val in attributes.items():
            escaped = self._escape_value(str(val))
            message += f" {key}='{escaped}'"
        message += "]"
        self._console.out(message)


class PyCharmReporter(PluginConfig):
    plugin = PyCharmReporterPlugin

    # Show internal calls in the traceback output
    show_internal_calls: bool = False

    # Show skipped scenarios
    show_skipped: bool = False
