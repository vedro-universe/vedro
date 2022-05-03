import json
import os
from traceback import format_exception
from types import TracebackType
from typing import Any, Callable, Dict, Generator, List, Tuple, Type, Union

from rich.console import Console
from rich.status import Status
from rich.style import Style
from rich.traceback import Traceback

import vedro
from vedro.core import Dispatcher, PluginConfig, ScenarioResult, StepResult
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
from .utils import make_console

__all__ = ("RichReporterPlugin", "RichReporter",)


ScenarioEndEventType = Union[ScenarioPassedEvent, ScenarioFailedEvent, ScenarioSkippedEvent]


class RichReporterPlugin(Reporter):
    def __init__(self, config: Type["RichReporter"], *,
                 console_factory: Callable[[], Console] = make_console) -> None:
        super().__init__(config)
        self._console = console_factory()
        self._verbosity = 0
        self._tb_pretty = config.tb_pretty
        self._tb_show_internal_calls = config.tb_show_internal_calls
        self._tb_show_locals = config.tb_show_locals
        self._tb_max_frames = config.tb_max_frames
        self._show_timings = config.show_timings
        self._show_paths = config.show_paths
        self._show_scenario_spinner = config.show_scenario_spinner
        self._scenario_spinner: Union[Status, None] = None
        self._namespace: Union[str, None] = None
        self._buffer: List[ScenarioResult] = []
        self._reruns = 0

    def subscribe(self, dispatcher: Dispatcher) -> None:
        super().subscribe(dispatcher)
        dispatcher.listen(DirectorInitEvent, lambda e: e.director.register("rich", self))

    def on_chosen(self) -> None:
        assert isinstance(self._dispatcher, Dispatcher)
        self._dispatcher.listen(ArgParseEvent, self.on_arg_parse) \
                        .listen(ArgParsedEvent, self.on_arg_parsed) \
                        .listen(StartupEvent, self.on_startup) \
                        .listen(ScenarioRunEvent, self.on_scenario_run) \
                        .listen(ScenarioSkippedEvent, self.on_scenario_end) \
                        .listen(ScenarioPassedEvent, self.on_scenario_end) \
                        .listen(ScenarioFailedEvent, self.on_scenario_end) \
                        .listen(CleanupEvent, self.on_cleanup)

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        group = event.arg_parser.add_argument_group("Rich Reporter")

        help_message = ("Increase verbosity level "
                        "(-v: show steps, -vv: show exception, -vvv: show scope)")
        group.add_argument("-v", "--verbose",
                           action="count",
                           default=self._verbosity,
                           help=help_message)
        group.add_argument("--show-timings",
                           action="store_true",
                           default=self._show_timings,
                           help="Show the elapsed time of each scenario")
        group.add_argument("--show-paths",
                           action="store_true",
                           default=self._show_paths,
                           help="Show the relative path of each passed scenario")
        group.add_argument("--tb-show-internal-calls",
                           action="store_true",
                           default=self._tb_show_internal_calls,
                           help="Show internal calls in the traceback output")
        group.add_argument("--tb-show-locals",
                           action="store_true",
                           default=self._tb_show_locals,
                           help="Show local variables in the traceback output")

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        self._verbosity = event.args.verbose
        self._show_timings = event.args.show_timings
        self._show_paths = event.args.show_paths
        self._tb_show_internal_calls = event.args.tb_show_internal_calls
        self._tb_show_locals = event.args.tb_show_locals
        self._reruns = event.args.reruns

    def on_startup(self, event: StartupEvent) -> None:
        self._console.out("Scenarios")

    def on_scenario_run(self, event: ScenarioRunEvent) -> None:
        if event.scenario_result.scenario.namespace != self._namespace:
            self._namespace = event.scenario_result.scenario.namespace
            namespace = self._namespace.replace("_", " ").replace("/", " / ")
            self._console.out(f"* {namespace}", style=Style(bold=True))
        if self._show_scenario_spinner:
            self._scenario_spinner = self._console.status(event.scenario_result.scenario.subject)
            self._scenario_spinner.start()

    def on_scenario_end(self, event: ScenarioEndEventType) -> None:
        if self._scenario_spinner:
            self._scenario_spinner.stop()
            self._scenario_spinner = None

        if not event.scenario_result.is_failed() and len(self._buffer) == 0:
            self._buffer.append(event.scenario_result)
            self._print_buffered()
        else:
            self._buffer.append(event.scenario_result)
            if event.scenario_result.rerun == self._reruns:
                self._print_buffered()

    def _print_scenario_skipped(self, scenario_result: ScenarioResult, *, indent: int = 0) -> None:
        pass

    def _print_scenario_passed(self, scenario_result: ScenarioResult, *, indent: int = 0) -> None:
        self._print_scenario_subject(scenario_result, self._show_timings)
        if self._show_paths:
            prepend = " " * indent
            rel_path = scenario_result.scenario.path.relative_to(os.getcwd())
            self._console.out(f"{prepend}   > {rel_path}", style=Style(color="grey50"))

    def _print_scenario_failed(self, scenario_result: ScenarioResult, *, indent: int = 0) -> None:
        self._print_scenario_subject(scenario_result, self._show_timings)

        if self._verbosity > 0:
            for step_result in scenario_result.step_results:
                self._print_step_name(step_result, indent=4 + indent)

        if self._verbosity > 1:
            for step_result in scenario_result.step_results:
                if step_result.exc_info:
                    self._print_exception(step_result.exc_info.value,
                                          step_result.exc_info.traceback)

        if self._verbosity > 2:
            if scenario_result.scope:
                self._print_scope(scenario_result.scope)
                self._console.out(" ")

    def _find_resolution(self, scenario_results: List[ScenarioResult]) -> ScenarioResult:
        passed, failed = [], []
        for scenario_result in scenario_results:
            if scenario_result.is_passed():
                passed.append(scenario_result)
            else:
                failed.append(scenario_result)
        return passed[-1] if len(passed) > len(failed) else failed[-1]

    def _print_scenario_result(self, scenario_result: ScenarioResult, *, indent: int = 0) -> None:
        if scenario_result.is_passed():
            self._print_scenario_passed(scenario_result, indent=indent)
        elif scenario_result.is_failed():
            self._print_scenario_failed(scenario_result, indent=indent)
        else:
            self._print_scenario_skipped(scenario_result, indent=indent)

    def _print_buffered(self) -> None:
        if len(self._buffer) == 1:
            return self._print_scenario_result(self._buffer.pop())

        resolution = self._find_resolution(self._buffer)
        self._print_scenario_subject(resolution)

        for rerun in range(1, len(self._buffer) + 1):
            scenario_result = self._buffer.pop(0)
            prefix = f" ├─[{rerun}/{self._reruns + 1}]"
            self._console.out(" │")
            self._console.out(prefix, end="")
            self._print_scenario_result(scenario_result, indent=len(prefix))

        self._console.out(" ")

    def _print_scenario_subject(self, scenario_result: ScenarioResult,
                                show_timings: bool = False) -> None:
        if scenario_result.is_passed():
            subject = f" ✔ {scenario_result.scenario.subject}"
            style = Style(color="green")
        elif scenario_result.is_failed():
            subject = f" ✗ {scenario_result.scenario.subject}"
            style = Style(color="red")
        else:
            return

        if show_timings:
            self._console.out(subject, style=style, end="")
            self._console.out(f" ({scenario_result.elapsed:.2f}s)", style=Style(color="grey50"))
        else:
            self._console.out(subject, style=style)

    def _print_step_name(self, step_result: StepResult, *, indent: int = 0) -> None:
        prepend = " " * indent
        if step_result.is_passed():
            name = f"{prepend}✔ {step_result.step_name}"
            style = Style(color="green")
        elif step_result.is_failed():
            name = f"{prepend}✗ {step_result.step_name}"
            style = Style(color="red")
        else:
            return

        if self._show_timings:
            self._console.out(name, style=style, end="")
            self._console.out(f" ({step_result.elapsed:.2f}s)", style=Style(color="grey50"))
        else:
            self._console.out(name, style=style)

    def _filter_locals(self, local_variables: Dict[str, Any]) -> Dict[str, Any]:
        filtered_locals = {}
        for key, val in local_variables.items():
            # self is always "Scenario"
            if key == "self":
                continue
            # assertion rewriter stuff
            if key.startswith("@"):
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

        if self._tb_pretty:
            trace = Traceback.extract(type(exception), exception, traceback,
                                      show_locals=self._tb_show_locals)
            for stack in trace.stacks:
                for frame in stack.frames:
                    if frame.locals:
                        frame.locals = self._filter_locals(frame.locals)
            self._console.print(Traceback(trace,
                                          max_frames=self._tb_max_frames, word_wrap=True))
            self._console.out(" ")
        else:
            formatted = format_exception(type(exception), exception, traceback,
                                         limit=self._tb_max_frames)
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

    def on_cleanup(self, event: CleanupEvent) -> None:
        if event.report.failed == 0 and event.report.passed > 0:
            style = Style(color="green", bold=True)
        else:
            style = Style(color="red", bold=True)
        self._console.out(" ")

        if len(event.report.summary) > 0:
            summary = "# " + "\n# ".join(event.report.summary)
            self._console.out(summary, style=Style(color="grey70"))

        if event.report.total == 1:
            scenario = "scenario"
        else:
            scenario = "scenarios"
        self._console.out(f"# {event.report.total} {scenario}, "
                          f"{event.report.passed} passed, "
                          f"{event.report.failed} failed, "
                          f"{event.report.skipped} skipped",
                          style=style,
                          end="")
        self._console.out(f" ({event.report.elapsed:.2f}s)", style=Style(color="blue"))


class RichReporter(PluginConfig):
    plugin = RichReporterPlugin

    # Show the elapsed time of each scenario
    show_timings: bool = False

    # Show the relative path of each passed scenario
    show_paths: bool = False

    # Show status indicator of the current running scenario
    show_scenario_spinner: bool = False

    # Show pretty traceback
    tb_pretty: bool = True

    # Show internal calls in the traceback output
    tb_show_internal_calls: bool = False

    # Show local variables in the traceback output
    tb_show_locals: bool = False

    # Max stack trace entries to show
    tb_max_frames: int = 8
