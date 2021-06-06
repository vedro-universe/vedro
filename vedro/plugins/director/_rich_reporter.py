import json
import os
import shutil
from traceback import format_exception
from typing import Any, Callable

from rich.console import Console
from rich.style import Style

from ..._core import Dispatcher
from ..._events import (
    ArgParsedEvent,
    ArgParseEvent,
    CleanupEvent,
    ScenarioFailEvent,
    ScenarioPassEvent,
    ScenarioRunEvent,
    ScenarioSkipEvent,
    StartupEvent,
)
from ._reporter import Reporter

__all__ = ("RichReporter",)


def get_terminal_size(default_columns: int = 80, default_lines: int = 24) -> os.terminal_size:
    columns, lines = shutil.get_terminal_size()
    # Fix columns=0 lines=0 in Pycharm
    if columns <= 0:
        columns = default_columns
    if lines <= 0:
        lines = default_lines
    return os.terminal_size((columns, lines))


def make_console(**options: Any) -> Console:
    size = get_terminal_size()
    return Console(**{
        "highlight": False,
        "force_terminal": True,
        "markup": False,
        "emoji": False,
        "width": size.columns,
        "height": size.lines,
        **options,
    })  # type: ignore


class RichReporter(Reporter):
    def __init__(self, console_factory: Callable[[], Console] = make_console) -> None:
        self._console_factory = console_factory
        self._verbosity = 0
        self._namespace = None

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ArgParseEvent, self.on_arg_parse) \
                  .listen(ArgParsedEvent, self.on_arg_parsed) \
                  .listen(StartupEvent, self.on_startup) \
                  .listen(ScenarioRunEvent, self.on_scenario_run) \
                  .listen(ScenarioSkipEvent, self.on_scenario_skip) \
                  .listen(ScenarioPassEvent, self.on_scenario_pass) \
                  .listen(ScenarioFailEvent, self.on_scenario_fail) \
                  .listen(CleanupEvent, self.on_cleanup)

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        event.arg_parser.add_argument("-v", "--verbose", action="count", default=self._verbosity)

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        self._verbosity = event.args.verbose
        self._console = self._console_factory()

    def on_startup(self, event: StartupEvent) -> None:
        self._console.print("Scenarios")

    def on_scenario_skip(self, event: ScenarioSkipEvent) -> None:
        pass

    def on_scenario_run(self, event: ScenarioRunEvent) -> None:
        if event.scenario_result.scenario_namespace != self._namespace:
            self._namespace = event.scenario_result.scenario_namespace
            self._console.print(f"* {self._namespace}", style=Style(bold=True))

    def on_scenario_pass(self, event: ScenarioPassEvent) -> None:
        subject = event.scenario_result.scenario_subject
        self._console.print(f" ✔ {subject}", style=Style(color="green"))

    def on_scenario_fail(self, event: ScenarioFailEvent) -> None:
        subject = event.scenario_result.scenario_subject
        self._console.print(f" ✗ {subject}", style=Style(color="red"))

        if self._verbosity > 0:
            for step_result in event.scenario_result.step_results:
                if step_result.is_passed():
                    self._console.print(f"    ✔ {step_result.step_name}",
                                        style=Style(color="green"))
                elif step_result.is_failed():
                    self._console.print(f"    ✗ {step_result.step_name}",
                                        style=Style(color="red"))

        if self._verbosity > 1:
            for step_result in event.scenario_result.step_results:
                if step_result.exc_info:
                    tb = format_exception(
                        step_result.exc_info.type,
                        step_result.exc_info.value,
                        step_result.exc_info.traceback,
                    )
                    self._console.print("".join(tb), style=Style(color="yellow"))

        if self._verbosity > 2:
            if event.scenario_result.scope:
                self._console.print("Scope:", style=Style(color="blue", bold=True))
                for key, val in event.scenario_result.scope.items():
                    self._console.print(f" {key}: ", end="", style=Style(color="blue"))
                    try:
                        val_repr = json.dumps(val, ensure_ascii=False, indent=4)
                    except:  # noqa: E722
                        val_repr = repr(val)
                    self._console.print(val_repr)
                self._console.print()

    def on_cleanup(self, event: CleanupEvent) -> None:
        if event.report.failed == 0 and event.report.passed > 0:
            style = Style(color="green", bold=True)
        else:
            style = Style(color="red", bold=True)
        self._console.print()
        self._console.print(f"# {event.report.total} scenarios, "
                            f"{event.report.failed} failed, "
                            f"{event.report.skipped} skipped ",
                            style=style,
                            end="")
        elapsed = 0.0
        self._console.print(f"({elapsed:.2f}s)", style=Style(color="blue"))
