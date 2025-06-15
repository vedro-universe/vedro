import sys
from types import ModuleType
from typing import Callable, Tuple, Type, Union, final

import vedro
from vedro.core import Dispatcher, ExcInfo, PluginConfig, ScenarioResult, StepResult
from vedro.events import (
    ArgParsedEvent,
    ArgParseEvent,
    CleanupEvent,
    ScenarioFailedEvent,
    ScenarioPassedEvent,
    ScenarioReportedEvent,
    ScenarioRunEvent,
    ScenarioSkippedEvent,
    StartupEvent,
)
from vedro.plugins.director._director_init_event import DirectorInitEvent
from vedro.plugins.director._reporter import Reporter

from ._rich_printer import RichPrinter
from .utils import TracebackFilter

__all__ = ("RichReporterPlugin", "RichReporter",)


@final
class RichReporterPlugin(Reporter):
    def __init__(self, config: Type["RichReporter"], *,
                 printer_factory: Callable[[], RichPrinter] = RichPrinter) -> None:
        super().__init__(config)
        self._printer = printer_factory()
        self._verbosity = 0
        self._tb_pretty = config.tb_pretty
        self._tb_show_internal_calls = config.tb_show_internal_calls
        self._tb_show_locals = config.tb_show_locals
        self._scope_width = config.scope_width
        self._tb_max_frames = config.tb_max_frames
        self._tb_width = config.tb_width
        self._tb_suppress_modules = config.tb_suppress_modules
        self._show_scenario_extras = config.show_scenario_extras
        self._show_step_extras = config.show_step_extras
        self._show_skipped = config.show_skipped
        self._show_skip_reason = config.show_skip_reason
        self._show_timings = config.show_timings
        self._show_paths = config.show_paths
        self._show_steps = config.show_steps
        self._hide_namespaces = config.hide_namespaces
        self._show_scenario_spinner = config.show_scenario_spinner
        self._show_discovering_spinner = False
        self._show_interrupted_traceback = config.show_interrupted_traceback
        self._show_scope = config.show_scope
        self._show_full_diff = config.show_full_diff
        self._v2_verbosity = config.v2_verbosity
        self._ring_bell = config.ring_bell
        self._namespace: Union[str, None] = None
        self._tb_filter: Union[TracebackFilter, None] = None

    def subscribe(self, dispatcher: Dispatcher) -> None:
        super().subscribe(dispatcher)
        dispatcher.listen(DirectorInitEvent, lambda e: e.director.register("rich", self))

    def on_chosen(self) -> None:
        assert isinstance(self._dispatcher, Dispatcher)

        self._dispatcher.listen(ArgParseEvent, self.on_arg_parse) \
                        .listen(ArgParsedEvent, self.on_arg_parsed) \
                        .listen(StartupEvent, self.on_startup) \
                        .listen(ScenarioRunEvent, self.on_scenario_run) \
                        .listen(ScenarioPassedEvent, self.on_scenario_end) \
                        .listen(ScenarioFailedEvent, self.on_scenario_end) \
                        .listen(ScenarioSkippedEvent, self.on_scenario_skipped) \
                        .listen(ScenarioReportedEvent, self.on_scenario_reported) \
                        .listen(CleanupEvent, self.on_cleanup)

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        group = event.arg_parser.add_argument_group("Rich Reporter")

        if self._v2_verbosity:
            help_message = "Increase verbosity level (show scope)"
        else:
            help_message = ("Increase verbosity level "
                            "(-v: show steps, -vv: show exception, -vvv: show scope)")
        group.add_argument("-v", "--verbose",
                           action="count",
                           default=self._verbosity,
                           help=help_message)
        group.add_argument("-S", "--show-scope",
                           action="store_true",
                           default=self._show_scope,
                           help="Show a snapshot of crucial variables (Scope) "
                                "when a scenario fails")
        group.add_argument("--show-full-diff",
                           action="store_true",
                           default=self._show_full_diff,
                           help="Show full diff in assertion errors")
        group.add_argument("--show-timings",
                           action="store_true",
                           default=self._show_timings,
                           help="Show the elapsed time of each scenario")
        group.add_argument("--show-steps",
                           action="store_true",
                           default=self._show_steps,
                           help="Show scenario step names")
        group.add_argument("--show-paths",
                           action="store_true",
                           default=self._show_paths,
                           help="Show the relative path of each passed/failed scenario")
        group.add_argument("--show-scenario-spinner",
                           action="store_true",
                           default=self._show_scenario_spinner,
                           help="Show scenario spinner")
        group.add_argument("--hide-namespaces",
                           action="store_true",
                           default=self._hide_namespaces,
                           help="Don't show scenario namespaces")
        group.add_argument("--tb-show-internal-calls",
                           action="store_true",
                           default=self._tb_show_internal_calls,
                           help="Show internal calls in the traceback output")
        group.add_argument("--tb-show-locals",
                           action="store_true",
                           default=self._tb_show_locals,
                           help="Show local variables in the traceback output")
        group.add_argument("-B", "--bell",
                           action="store_true",
                           default=self._ring_bell,
                           dest="ring_bell",
                           help="Trigger a 'bell' sound at the end of scenario execution")

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        self._verbosity = event.args.verbose
        self._show_scope = event.args.show_scope

        if self._v2_verbosity:
            self._verbosity = self._verbosity + 2

        if self._show_scope:
            self._verbosity = 3

        self._show_full_diff = event.args.show_full_diff
        self._show_timings = event.args.show_timings
        self._show_paths = event.args.show_paths
        self._show_steps = event.args.show_steps
        self._show_scenario_spinner = event.args.show_scenario_spinner
        self._hide_namespaces = event.args.hide_namespaces
        self._tb_show_internal_calls = event.args.tb_show_internal_calls
        self._tb_show_locals = event.args.tb_show_locals
        self._ring_bell = event.args.ring_bell

        if self._tb_max_frames < 4:
            raise ValueError("RichReporter: `tb_max_frames` must be >= 4")

        if self._tb_show_locals and (not self._tb_pretty):
            raise ValueError("RichReporter: to enable `tb_show_locals` set `tb_pretty` to `True`")

        if self._show_paths and (not self._show_scenario_extras):
            raise ValueError(
                "RichReporter: to enable `show_paths` set `show_scenario_extras` to `True`")

        if self._show_skip_reason and (not self._show_scenario_extras):
            raise ValueError(
                "RichReporter: to enable `show_skip_reason` set `show_scenario_extras` to `True`")

        if self._show_discovering_spinner:
            self._printer.show_spinner("Discovering scenarios...")

        if not self._tb_show_internal_calls:
            self._tb_suppress_modules = tuple(self._tb_suppress_modules) + (vedro,)
        else:
            self._tb_suppress_modules = tuple(self._tb_suppress_modules)
        try:
            self._tb_filter = TracebackFilter(self._tb_suppress_modules)
        except (AttributeError, TypeError):
            raise ValueError("RichReporter: `tb_suppress_modules` must be a tuple of modules")

    def on_startup(self, event: StartupEvent) -> None:
        if self._show_discovering_spinner:
            self._printer.hide_spinner()
        self._printer.print_header()

    def on_scenario_run(self, event: ScenarioRunEvent) -> None:
        self._print_namespace(event.scenario_result.scenario.namespace)
        if self._show_scenario_spinner:
            self._printer.show_spinner(f" {event.scenario_result.scenario.subject}")

    def _add_extra_details(self, scenario_result: ScenarioResult) -> None:
        if self._show_skip_reason and scenario_result.is_skipped():
            skip_reason = scenario_result.scenario.skip_reason
            if skip_reason:
                scenario_result.add_extra_details(f"{skip_reason}")

        if self._show_paths:
            scenario_result.add_extra_details(f"{scenario_result.scenario.rel_path}")

    def on_scenario_end(self, event: Union[ScenarioPassedEvent, ScenarioFailedEvent]) -> None:
        self._add_extra_details(event.scenario_result)

    def on_scenario_skipped(self, event: ScenarioSkippedEvent) -> None:
        self._add_extra_details(event.scenario_result)
        if not self._show_skipped:
            return
        self._print_namespace(event.scenario_result.scenario.namespace)

    def _print_exception(self, exc_info: ExcInfo) -> None:
        if self._tb_suppress_modules:
            assert self._tb_filter
            traceback = self._tb_filter.filter_tb(exc_info.traceback)
            exc_info = ExcInfo(exc_info.type, exc_info.value, traceback)

        if self._tb_pretty and not self._is_exception_group(exc_info):
            self._printer.print_pretty_exception(exc_info,
                                                 width=self._tb_width,
                                                 max_frames=self._tb_max_frames,
                                                 show_locals=self._tb_show_locals,
                                                 show_internal_calls=True,
                                                 show_full_diff=self._show_full_diff)
        else:
            self._printer.print_exception(exc_info,
                                          max_frames=self._tb_max_frames,
                                          show_internal_calls=True)

    def _is_exception_group(self, exc_info: ExcInfo) -> bool:
        # WORKAROUND: This logic is in place as a temporary solution until
        # https://github.com/vedro-universe/vedro/issues/113 is resolved.
        if sys.version_info >= (3, 11):
            return isinstance(exc_info.value, ExceptionGroup)  # noqa: F821
        return False

    def _prefix_to_indent(self, prefix: str, indent: int = 0) -> str:
        last_line = prefix.split("\n")[-1]
        return (len(last_line) + indent) * " "

    def _print_namespace(self, namespace: str) -> None:
        if namespace != self._namespace:
            self._namespace = namespace
            if self._hide_namespaces is False:
                self._printer.print_namespace(namespace)

    def _print_scenario_extras(self, scenario_result: ScenarioResult, *, prefix: str = "") -> None:
        if not self._show_scenario_extras:
            return
        if scenario_result.extra_details:
            self._printer.print_scenario_extra_details(scenario_result.extra_details,
                                                       prefix=prefix)

    def _print_step_extras(self, step_result: StepResult, *, prefix: str = "") -> None:
        if not self._show_step_extras:
            return
        if step_result.extra_details:
            self._printer.print_step_extra_details(step_result.extra_details, prefix=prefix)

    def _print_scenario_passed(self, scenario_result: ScenarioResult, *, prefix: str = "") -> None:
        elapsed = scenario_result.elapsed if self._show_timings else None
        self._printer.print_scenario_subject(scenario_result.scenario.subject,
                                             scenario_result.status,
                                             elapsed=elapsed,
                                             prefix=prefix)

        self._print_scenario_extras(scenario_result,
                                    prefix=self._prefix_to_indent(prefix, indent=2))

        if self._show_steps:
            for step_result in scenario_result.step_results:
                elapsed = step_result.elapsed if self._show_timings else None
                step_prefix = self._prefix_to_indent(prefix, indent=2)
                self._printer.print_step_name(step_result.step_name, step_result.status,
                                              elapsed=elapsed, prefix=step_prefix)
                self._print_step_extras(step_result, prefix=step_prefix)

    def _print_scenario_failed(self, scenario_result: ScenarioResult, *, prefix: str = "") -> None:
        elapsed = scenario_result.elapsed if self._show_timings else None
        self._printer.print_scenario_subject(scenario_result.scenario.subject,
                                             scenario_result.status,
                                             elapsed=elapsed,
                                             prefix=prefix)

        self._print_scenario_extras(scenario_result,
                                    prefix=self._prefix_to_indent(prefix, indent=2))

        if self._verbosity > 0:
            for step_result in scenario_result.step_results:
                elapsed = step_result.elapsed if self._show_timings else None
                step_prefix = self._prefix_to_indent(prefix, indent=2)
                self._printer.print_step_name(step_result.step_name, step_result.status,
                                              elapsed=elapsed, prefix=step_prefix)
                self._print_step_extras(step_result, prefix=step_prefix)

        if self._verbosity > 1:
            for step_result in scenario_result.step_results:
                if step_result.exc_info:
                    self._print_exception(step_result.exc_info)

        if self._verbosity > 2:
            if scenario_result.scope:
                scope_width = self._scope_width or self._printer.console.size.width - 1
                self._printer.print_scope(scenario_result.scope, scope_width=scope_width)

    def _print_scenario_skipped(self, scenario_result: ScenarioResult, *,
                                prefix: str = "") -> None:
        if not self._show_skipped:
            return
        elapsed = scenario_result.elapsed if self._show_timings else None
        self._printer.print_scenario_subject(scenario_result.scenario.subject,
                                             scenario_result.status,
                                             elapsed=elapsed,
                                             prefix=prefix)

        self._print_scenario_extras(scenario_result,
                                    prefix=self._prefix_to_indent(prefix, indent=2))

    def _print_scenario_result(self, scenario_result: ScenarioResult, *, prefix: str = "") -> None:
        if scenario_result.is_passed():
            self._print_scenario_passed(scenario_result, prefix=prefix)
        elif scenario_result.is_failed():
            self._print_scenario_failed(scenario_result, prefix=prefix)
        elif scenario_result.is_skipped():
            self._print_scenario_skipped(scenario_result, prefix=prefix)

    def on_scenario_reported(self, event: ScenarioReportedEvent) -> None:
        if self._show_scenario_spinner:
            self._printer.hide_spinner()

        aggregated_result = event.aggregated_result
        rescheduled = len(aggregated_result.scenario_results)
        if rescheduled == 1:
            self._print_scenario_result(aggregated_result.scenario_results[0], prefix=" ")
            return

        self._printer.print_scenario_subject(aggregated_result.scenario.subject,
                                             aggregated_result.status, elapsed=None, prefix=" ")
        for index, scenario_result in enumerate(aggregated_result.scenario_results, start=1):
            prefix = f" │\n ├─[{index}/{rescheduled}] "
            self._print_scenario_result(scenario_result, prefix=prefix)

        self._printer.print_empty_line()

    def on_cleanup(self, event: CleanupEvent) -> None:
        self._printer.print_empty_line()

        is_interrupted = False
        if event.report.interrupted:
            is_interrupted = True
            self._printer.print_interrupted(event.report.interrupted,
                                            show_traceback=self._show_interrupted_traceback)

        self._printer.print_report_summary(event.report.summary)
        self._printer.print_report_stats(total=event.report.total,
                                         passed=event.report.passed,
                                         failed=event.report.failed,
                                         skipped=event.report.skipped,
                                         elapsed=event.report.elapsed,
                                         is_interrupted=is_interrupted)

        if self._ring_bell:
            self._printer.console.bell()


class RichReporter(PluginConfig):
    plugin = RichReporterPlugin
    description = "Enhanced, customizable scenario reporting with rich output"

    # Show scenario extra details
    show_scenario_extras: bool = True

    # Show step extra details
    show_step_extras: bool = True

    # Show skipped scenarios
    show_skipped: bool = True

    # Show reason of skipped scenarios
    # Available if `show_scenario_extras` and `show_skipped` is True
    show_skip_reason: bool = True

    # Show the elapsed time of each scenario
    show_timings: bool = False

    # Show the relative path of each executed scenario (passed, failed, or skipped)
    # Available if `show_scenario_extras` is True
    show_paths: bool = False

    # Show scenario step names
    show_steps: bool = False

    # Don't show scenario namespaces
    hide_namespaces: bool = False

    # Show status indicator of the current running scenario
    show_scenario_spinner: bool = False

    # Show pretty traceback
    tb_pretty: bool = True

    # Show internal calls in the traceback output
    tb_show_internal_calls: bool = False

    # Show local variables in the traceback output
    # Available if `tb_pretty` is True
    tb_show_locals: bool = False

    # Set the width of the traceback output
    # If None, terminal width will be used
    # Available if `tb_pretty` is True
    tb_width: Union[int, None] = 100

    # Max stack trace entries to show (min=4)
    tb_max_frames: int = 8

    # Suppress modules in the traceback output
    tb_suppress_modules: Tuple[Union[str, ModuleType], ...] = ()

    # Truncate lines in Scope based on scope_width value.
    # If scope_width is None, lines are truncated to the terminal's width.
    # If scope_width is -1, lines aren't truncated.
    # Otherwise, lines are truncated to the given length.
    scope_width: Union[int, None] = -1

    # Show traceback if the execution is interrupted
    show_interrupted_traceback: bool = False

    # Show a snapshot of crucial variables (Scope) when a test scenario fails
    show_scope: bool = False

    # Show full diff in assertion errors
    # Available if `tb_pretty` is True
    show_full_diff: bool = False

    # Enable new verbose levels
    v2_verbosity: bool = True

    # Trigger a 'bell' sound at the end of scenario execution
    # (if supported by the terminal)
    ring_bell: bool = False
