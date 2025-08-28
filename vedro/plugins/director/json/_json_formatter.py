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
TimeFunction = Callable[[], float]


class JsonFormatter:
    def __init__(self, traceback_filter: TracebackFilter, *,
                 time_fn: TimeFunction = time) -> None:
        self._tb_filter = traceback_filter
        self._time_fn = time_fn

    @property
    def tb_filter(self) -> TracebackFilter:
        return self._tb_filter

    @property
    def time_fn(self) -> TimeFunction:
        return self._time_fn

    def format_startup_event(self, discovered: int, scheduled: int, skipped: int,
                             rich_output: Optional[str] = None) -> StartupEventDict:
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
        event = {
            "event": "cleanup",
            "timestamp": self._format_timestamp(self._time_fn()),
            "report": {
                "total": report.total,
                "passed": report.passed,
                "failed": report.failed,
                "skipped": report.skipped,
                "elapsed": self._format_elapsed(report.elapsed),
                "interrupted": self.format_exc_info(report.interrupted),
            }
        }
        if rich_output:
            event["rich_output"] = rich_output
        return cast(CleanupEventDict, event)

    def format_scenario(self,
                        scenario: VirtualScenario,
                        status: ScenarioStatus,
                        elapsed: float) -> ScenarioDict:
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
        steps = []
        for step_result in step_results:
            steps.append({
                "name": step_result.step.name,
                "status": step_result.status.value,
                "elapsed": self._format_elapsed(step_result.elapsed),
                "error": self.format_exc_info(step_result.exc_info),
            })
        return cast(List[StepDict], steps)

    def _format_timestamp(self, timestamp: Union[float, None]) -> Union[int, None]:
        if timestamp is None:
            return None
        return int(timestamp * 1000)

    def _format_elapsed(self, elapsed: float) -> int:
        return int(elapsed * 1000)

    def format_exc_info(self, exc_info: Union[ExcInfo, None]) -> Union[ExcInfoDict, None]:
        if exc_info is None:
            return None

        file, lineno = None, None
        if exc_info.traceback is not None:
            file, lineno = self._get_traceback_lineno(exc_info.traceback)

        return cast(ExcInfoDict, {
            "type": exc_info.type.__name__,
            "message": str(exc_info.value),
            "file": file,
            "lineno": lineno,
        })

    def _get_traceback_lineno(self, traceback: TracebackType) -> TracebackLineInfo:
        tb = self._tb_filter.filter_tb(traceback)

        while tb.tb_next is not None:
            tb = tb.tb_next

        return tb.tb_frame.f_code.co_filename, tb.tb_lineno
