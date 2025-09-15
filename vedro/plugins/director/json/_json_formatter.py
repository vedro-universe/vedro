from time import time
from types import TracebackType
from typing import Callable, List, Optional, Tuple, Union, cast

from vedro.core import (
    AggregatedResult,
    ExcInfo,
    Report,
    ScenarioResult,
    ScenarioStatus,
    StepResult,
    VirtualScenario,
)
from vedro.core.exc_info import TracebackFilter

from ._event_types import (
    CleanupEventDict,
    ExcInfoDict,
    ScenarioDict,
    ScenarioEventDict,
    ScenarioReportedEventDict,
    StartupEventDict,
    StepDict,
)

__all__ = ("JsonFormatter",)

TracebackLineInfo = Tuple[Union[str, None], Union[int, None]]
"""
Defines the ``(file_path, line_number)`` pair extracted from a traceback.

This alias standardizes the minimal location information taken from the
terminal (last) traceback frame after filtering.
"""

TimeFunction = Callable[[], float]
"""
Defines the callable used to obtain the current time in seconds.

The formatter uses this function to generate timestamps and to convert
elapsed durations. It defaults to :func:`time.time` when not overridden.
"""


class JsonFormatter:
    """
    Formatter for converting test execution events and results to JSON-compatible dictionaries.

    This class provides methods to format various test lifecycle events (startup, scenario
    execution, cleanup) into structured dictionaries that can be easily serialized to JSON.
    It handles scenario results, step results, exception information, and timing data.
    """

    def __init__(self, traceback_filter: TracebackFilter, *,
                 time_fn: TimeFunction = time) -> None:
        """
        Initialize the JSON formatter.

        :param traceback_filter: Filter for processing exception tracebacks.
        :param time_fn: Function to get current timestamp (defaults to time.time).
                        Useful for testing with controlled time values.
        """
        self._tb_filter = traceback_filter
        self._time_fn = time_fn

    @property
    def tb_filter(self) -> TracebackFilter:
        """Get the traceback filter used for processing exceptions."""
        return self._tb_filter

    @property
    def time_fn(self) -> TimeFunction:
        """Get the time function used for generating timestamps."""
        return self._time_fn

    def format_startup_event(self, discovered: int, scheduled: int, skipped: int,
                             rich_output: Optional[str] = None) -> StartupEventDict:
        """
        Format the test suite startup event.

        :param discovered: Number of scenarios discovered.
        :param scheduled: Number of scenarios scheduled for execution.
        :param skipped: Number of scenarios skipped.
        :param rich_output: Optional rich output content to include.
        :return: Dictionary containing formatted startup event data.
        """
        event = {
            "event": "startup",
            "timestamp": self._format_timestamp(self._time_fn()),
            "scenarios": {
                "discovered": discovered,
                "scheduled": scheduled,
                "skipped": skipped,
            }
        }
        if rich_output:
            event["rich_output"] = rich_output
        return cast(StartupEventDict, event)

    def format_scenario_run_event(self, scenario_result: ScenarioResult,
                                  rich_output: Optional[str] = None) -> ScenarioEventDict:
        """
        Format a scenario run event (scenario has started executing).

        :param scenario_result: The scenario result object.
        :param rich_output: Optional rich output content to include.
        :return: Dictionary containing formatted scenario run event data.
        """
        event = {
            "event": "scenario_run",
            "timestamp": self._format_timestamp(self._time_fn()),
            "scenario": self.format_scenario(
                scenario_result.scenario,
                scenario_result.status,
                scenario_result.elapsed
            )
        }
        if rich_output:
            event["rich_output"] = rich_output
        return cast(ScenarioEventDict, event)

    def format_scenario_passed_event(self, scenario_result: ScenarioResult,
                                     rich_output: Optional[str] = None) -> ScenarioEventDict:
        """
        Format a scenario passed event.

        :param scenario_result: The scenario result object for the passed scenario.
        :param rich_output: Optional rich output content to include.
        :return: Dictionary containing formatted scenario passed event data.
        """
        event = {
            "event": "scenario_passed",
            "timestamp": self._format_timestamp(self._time_fn()),
            "scenario": self.format_scenario(
                scenario_result.scenario,
                scenario_result.status,
                scenario_result.elapsed
            )
        }
        if rich_output:
            event["rich_output"] = rich_output
        return cast(ScenarioEventDict, event)

    def format_scenario_failed_event(self, scenario_result: ScenarioResult,
                                     rich_output: Optional[str] = None) -> ScenarioEventDict:
        """
        Format a scenario failed event.

        :param scenario_result: The scenario result object for the failed scenario.
        :param rich_output: Optional rich output content to include.
        :return: Dictionary containing formatted scenario failed event data.
        """
        event = {
            "event": "scenario_failed",
            "timestamp": self._format_timestamp(self._time_fn()),
            "scenario": self.format_scenario(
                scenario_result.scenario,
                scenario_result.status,
                scenario_result.elapsed
            )
        }
        if rich_output:
            event["rich_output"] = rich_output
        return cast(ScenarioEventDict, event)

    def format_scenario_skipped_event(self, scenario_result: ScenarioResult,
                                      rich_output: Optional[str] = None) -> ScenarioEventDict:
        """
        Format a scenario skipped event.

        :param scenario_result: The scenario result object for the skipped scenario.
        :param rich_output: Optional rich output content to include.
        :return: Dictionary containing formatted scenario skipped event data.
        """
        event = {
            "event": "scenario_skipped",
            "timestamp": self._format_timestamp(self._time_fn()),
            "scenario": self.format_scenario(
                scenario_result.scenario,
                scenario_result.status,
                scenario_result.elapsed
            )
        }
        if rich_output:
            event["rich_output"] = rich_output
        return cast(ScenarioEventDict, event)

    def format_scenario_reported_event(self,
                                       aggregated_result: AggregatedResult,
                                       rich_output: Optional[str] = None
                                       ) -> ScenarioReportedEventDict:
        """
        Format a scenario reported event with detailed step information.

        This event includes complete scenario execution details including all step results.

        :param aggregated_result: The aggregated result containing scenario and step data.
        :param rich_output: Optional rich output content to include.
        :return: Dictionary containing formatted scenario reported event data with steps.
        """
        event = {
            "event": "scenario_reported",
            "timestamp": self._format_timestamp(self._time_fn()),
            "scenario": self.format_scenario(
                aggregated_result.scenario,
                aggregated_result.status,
                aggregated_result.elapsed
            ),
            "steps": self._format_steps(aggregated_result.step_results),
        }
        if rich_output:
            event["rich_output"] = rich_output
        return cast(ScenarioReportedEventDict, event)

    def format_cleanup_event(self, report: Report,
                             rich_output: Optional[str] = None) -> CleanupEventDict:
        """
        Format the test suite cleanup event with final report summary.

        :param report: The final test report containing execution summary.
        :param rich_output: Optional rich output content to include.
        :return: Dictionary containing formatted cleanup event data with report summary.
        """
        interrupted = None
        if report.interrupted:
            interrupted = self.format_exc_info(report.interrupted)
        event = {
            "event": "cleanup",
            "timestamp": self._format_timestamp(self._time_fn()),
            "report": {
                "total": report.total,
                "passed": report.passed,
                "failed": report.failed,
                "skipped": report.skipped,
                "elapsed": self._format_elapsed(report.elapsed),
                "interrupted": interrupted,
            }
        }
        if rich_output:
            event["rich_output"] = rich_output
        return cast(CleanupEventDict, event)

    def format_scenario(self,
                        scenario: VirtualScenario,
                        status: ScenarioStatus,
                        elapsed: float) -> ScenarioDict:
        """
        Format scenario information into a dictionary.

        :param scenario: The virtual scenario object.
        :param status: The execution status of the scenario.
        :param elapsed: Time elapsed during scenario execution in seconds.
        :return: Dictionary containing formatted scenario data.
        """
        return {
            "id": scenario.unique_id,
            "subject": scenario.subject,
            "path": str(scenario.path),
            "lineno": scenario.lineno,
            "status": status.value,
            "elapsed": self._format_elapsed(elapsed),
            "skip_reason": scenario.skip_reason if scenario.is_skipped() else None,
        }

    def _format_steps(self, step_results: List[StepResult]) -> List[StepDict]:
        """
        Format a list of step results into dictionaries.

        :param step_results: List of step result objects.
        :return: List of dictionaries containing formatted step data.
        """
        steps = []
        for step_result in step_results:
            error = None
            if step_result.exc_info is not None:
                error = self.format_exc_info(step_result.exc_info)
            steps.append({
                "name": step_result.step.name,
                "status": step_result.status.value,
                "elapsed": self._format_elapsed(step_result.elapsed),
                "error": error,
            })
        return cast(List[StepDict], steps)

    def _format_timestamp(self, timestamp: Union[float, None]) -> Union[int, None]:
        """
        Convert timestamp from seconds to milliseconds.

        :param timestamp: Timestamp in seconds (float) or None.
        :return: Timestamp in milliseconds (int) or None.
        """
        if timestamp is None:
            return None
        return int(timestamp * 1000)

    def _format_elapsed(self, elapsed: float) -> int:
        """
        Convert elapsed time from seconds to milliseconds.

        :param elapsed: Elapsed time in seconds.
        :return: Elapsed time in milliseconds.
        """
        return int(elapsed * 1000)

    def format_exc_info(self, exc_info: ExcInfo) -> Union[ExcInfoDict, None]:
        """
        Format exception information into a dictionary.

        Extracts the exception type, message, and location (file and line number)
        from the traceback.

        :param exc_info: Exception information object containing type, value, and traceback.
        :return: Dictionary containing formatted exception data.
        """
        file, lineno = self._get_traceback_lineno(exc_info.traceback)
        return cast(ExcInfoDict, {
            "type": exc_info.type.__name__,
            "message": str(exc_info.value),
            "file": file,
            "lineno": lineno,
        })

    def _get_traceback_lineno(self, traceback: TracebackType) -> TracebackLineInfo:
        """
        Extract file path and line number from the last frame of a traceback.

        :param traceback: The traceback object to analyze.
        :return: Tuple of (file_path, line_number) from the last traceback frame.
        """
        tb = self._tb_filter.filter_tb(traceback)

        while tb.tb_next is not None:
            tb = tb.tb_next

        return tb.tb_frame.f_code.co_filename, tb.tb_lineno
