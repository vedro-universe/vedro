from traceback import format_exception
from typing import Callable, Union

from rich.console import Console
from rich.style import Style

from ...._core import Dispatcher
from ...._events import (
    ArgParsedEvent,
    ArgParseEvent,
    CleanupEvent,
    ScenarioFailEvent,
    ScenarioPassEvent,
    ScenarioRunEvent,
    ScenarioSkipEvent,
    StartupEvent,
)
from .._reporter import Reporter
from .utils import format_scope, make_console

__all__ = ("RichReporter",)


class RichReporter(Reporter):
    def __init__(self, console_factory: Callable[[], Console] = make_console) -> None:
        self._console = console_factory()
        self._verbosity = 0
        self._namespace: Union[str, None] = None

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

        if self._verbosity == 0:
            return

        for step_result in event.scenario_result.step_results:
            if step_result.is_passed():
                self._console.print(f"    ✔ {step_result.step_name}",
                                    style=Style(color="green"))
            elif step_result.is_failed():
                self._console.print(f"    ✗ {step_result.step_name}",
                                    style=Style(color="red"))

        if self._verbosity == 1:
            return

        for step_result in event.scenario_result.step_results:
            if step_result.exc_info:
                tb = format_exception(
                    step_result.exc_info.type,
                    step_result.exc_info.value,
                    step_result.exc_info.traceback,
                )
                self._console.print("".join(tb), style=Style(color="yellow"))

        if self._verbosity == 2:
            return

        if event.scenario_result.scope:
            self._console.print("Scope:", style=Style(color="blue", bold=True))
            for key, val in format_scope(event.scenario_result.scope):
                self._console.print(f" {key}: ", end="", style=Style(color="blue"))
                self._console.print(val)
            self._console.print()

    def on_cleanup(self, event: CleanupEvent) -> None:
        if event.report.failed == 0 and event.report.passed > 0:
            style = Style(color="green", bold=True)
        else:
            style = Style(color="red", bold=True)
        self._console.print()
        self._console.print(f"# {event.report.total} scenarios, "
                            f"{event.report.passed} passed, "
                            f"{event.report.failed} failed, "
                            f"{event.report.skipped} skipped",
                            style=style,
                            end="")
        self._console.print(f" ({event.report.elapsed:.2f}s)", style=Style(color="blue"))
