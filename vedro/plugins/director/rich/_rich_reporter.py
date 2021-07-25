import json
import os
from traceback import format_exception
from types import TracebackType
from typing import Any, Callable, Dict, Generator, Tuple, Union

from rich.console import Console
from rich.style import Style
from rich.traceback import Traceback

import vedro
from vedro.core import Dispatcher, ScenarioResult, StepResult
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

from .._reporter import Reporter
from .utils import make_console

__all__ = ("RichReporter",)


class RichReporter(Reporter):
    def __init__(self, console_factory: Callable[[], Console] = make_console) -> None:
        self._console = console_factory()
        self._verbosity = 0
        self._tb_show_internal_calls = False
        self._tb_show_locals = False
        self._show_timings = False
        self._namespace: Union[str, None] = None

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ArgParseEvent, self.on_arg_parse) \
                  .listen(ArgParsedEvent, self.on_arg_parsed) \
                  .listen(StartupEvent, self.on_startup) \
                  .listen(ScenarioRunEvent, self.on_scenario_run) \
                  .listen(ScenarioSkippedEvent, self.on_scenario_skipped) \
                  .listen(ScenarioPassedEvent, self.on_scenario_passed) \
                  .listen(ScenarioFailedEvent, self.on_scenario_failed) \
                  .listen(CleanupEvent, self.on_cleanup)

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        help_message = ("Increase verbosity level "
                        "(-v: show steps, -vv: show exception, -vvv: show scope)")
        event.arg_parser.add_argument("-v", "--verbose",
                                      action="count",
                                      default=self._verbosity,
                                      help=help_message)
        event.arg_parser.add_argument("--show-timings",
                                      action='store_true',
                                      default=False,
                                      help="Show the elapsed time of each scenario")
        event.arg_parser.add_argument("--tb-show-internal-calls",
                                      action='store_true',
                                      default=False,
                                      help="Show internal calls in the traceback output")
        event.arg_parser.add_argument("--tb-show-locals",
                                      action='store_true',
                                      default=False,
                                      help="Show local variables in the traceback output")

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        self._verbosity = event.args.verbose
        self._show_timings = event.args.show_timings
        self._tb_show_internal_calls = event.args.tb_show_internal_calls
        self._tb_show_locals = event.args.tb_show_locals

    def on_startup(self, event: StartupEvent) -> None:
        self._console.out("Scenarios")

    def on_scenario_skipped(self, event: ScenarioSkippedEvent) -> None:
        pass

    def on_scenario_run(self, event: ScenarioRunEvent) -> None:
        if event.scenario_result.scenario_namespace != self._namespace:
            self._namespace = event.scenario_result.scenario_namespace
            self._console.out(f"* {self._namespace}", style=Style(bold=True))

    def _print_scenario_subject(self, scenario_result: ScenarioResult) -> None:
        template_index = scenario_result.scenario.template_index
        templated = f"[{template_index}] " if (template_index is not None) else ""

        if scenario_result.is_passed():
            subject = f" ✔ {templated}{scenario_result.scenario_subject}"
            style = Style(color="green")
        elif scenario_result.is_failed():
            subject = f" ✗ {templated}{scenario_result.scenario_subject}"
            style = Style(color="red")
        else:
            return

        if self._show_timings:
            self._console.out(subject, style=style, end="")
            self._console.out(f" ({scenario_result.elapsed:.2f}s)", style=Style(color="grey50"))
        else:
            self._console.out(subject, style=style)

    def _print_step_name(self, step_result: StepResult) -> None:
        if step_result.is_passed():
            name = f"    ✔ {step_result.step_name}"
            style = Style(color="green")
        elif step_result.is_failed():
            name = f"    ✗ {step_result.step_name}"
            style = Style(color="red")
        else:
            return

        if self._show_timings:
            self._console.out(name, style=style, end="")
            self._console.out(f" ({step_result.elapsed:.2f}s)", style=Style(color="grey50"))
        else:
            self._console.out(name, style=style)

    def on_scenario_passed(self, event: ScenarioPassedEvent) -> None:
        self._print_scenario_subject(event.scenario_result)

    def _filter_locals(self, local_variables: Dict[str, Any]) -> Dict[str, Any]:
        filtered_locals = {}
        for key, val in local_variables.items():
            # self is always "Scenario"
            if key == "self":
                continue
            # assertion rewriter stuff
            if key.startswith("@py"):
                continue
            filtered_locals[key] = val
        return filtered_locals

    def _print_exception(self, exception: BaseException, traceback: TracebackType) -> None:
        if not self._tb_show_internal_calls:
            root = os.path.dirname(vedro.__file__)
            while traceback.tb_next is not None:
                filename = os.path.abspath(traceback.tb_frame.f_code.co_filename)
                if os.path.commonpath([root, filename]) != root:
                    break
                traceback = traceback.tb_next

        if self._tb_show_locals:
            trace = Traceback.extract(type(exception), exception, traceback, show_locals=True)
            for stack in trace.stacks:
                for frame in stack.frames:
                    if frame.locals:
                        frame.locals = self._filter_locals(frame.locals)
            self._console.print(Traceback(trace))
            self._console.out(" ")
        else:
            formatted = format_exception(type(exception), exception, traceback)
            self._console.out("".join(formatted), style=Style(color="yellow"))

    def _format_scope(self, scope: Dict[Any, Any]) -> Generator[Tuple[str, str], None, None]:
        for key, val in scope.items():
            try:
                val_repr = json.dumps(val, ensure_ascii=False, indent=4)
            except:  # noqa: E722
                val_repr = repr(val)
            yield str(key), val_repr

    def _print_scope(self, scope: Dict[Any, Any]) -> None:
        self._console.out("Scope:", style=Style(color="blue", bold=True))
        for key, val in self._format_scope(scope):
            self._console.out(f" {key}: ", end="", style=Style(color="blue"))
            self._console.out(val)

    def on_scenario_failed(self, event: ScenarioFailedEvent) -> None:
        self._print_scenario_subject(event.scenario_result)

        if self._verbosity > 0:
            for step_result in event.scenario_result.step_results:
                self._print_step_name(step_result)

        if self._verbosity > 1:
            for step_result in event.scenario_result.step_results:
                if step_result.exc_info:
                    self._print_exception(step_result.exc_info.value,
                                          step_result.exc_info.traceback)

        if self._verbosity > 2:
            if event.scenario_result.scope:
                self._print_scope(event.scenario_result.scope)
                self._console.out(" ")

    def on_cleanup(self, event: CleanupEvent) -> None:
        if event.report.failed == 0 and event.report.passed > 0:
            style = Style(color="green", bold=True)
        else:
            style = Style(color="red", bold=True)
        self._console.out(" ")

        if len(event.report.summary) > 0:
            summary = "# " + "\n# ".join(event.report.summary)
            self._console.out(summary, style=Style(color="grey70"))

        self._console.out(f"# {event.report.total} scenarios, "
                          f"{event.report.passed} passed, "
                          f"{event.report.failed} failed, "
                          f"{event.report.skipped} skipped",
                          style=style,
                          end="")
        self._console.out(f" ({event.report.elapsed:.2f}s)", style=Style(color="blue"))
