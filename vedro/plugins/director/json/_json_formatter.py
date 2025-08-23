from time import time
from types import TracebackType
from typing import Any, Dict, List, Tuple, Union

from vedro.core import (
    AggregatedResult,
    ExcInfo,
    ScenarioResult,
    ScenarioStatus,
    StepResult,
    VirtualScenario,
)
from vedro.core.exc_info import TracebackFilter

__all__ = ("JsonFormatter",)


class JsonFormatter:
    def __init__(self, traceback_filter: TracebackFilter) -> None:
        self._tb_filter = traceback_filter

    def format_startup_event(self,
                             discovered: int, scheduled: int, skipped: int) -> Dict[str, Any]:
        return {
            "event": "startup",
            "timestamp": self._format_timestamp(time()),
            "scenarios": {
                "discovered": discovered,
                "scheduled": scheduled,
                "skipped": skipped,
            }
        }

    def format_scenario_run_event(self, scenario_result: ScenarioResult) -> Dict[str, Any]:
        return {
            "event": "scenario_run",
            "timestamp": self._format_timestamp(time()),
            "scenario": self.format_scenario(
                scenario_result.scenario,
                scenario_result.status,
                scenario_result.elapsed
            )
        }

    def format_scenario_passed_event(self, scenario_result: ScenarioResult) -> Dict[str, Any]:
        return {
            "event": "scenario_passed",
            "timestamp": self._format_timestamp(time()),
            "scenario": self.format_scenario(
                scenario_result.scenario,
                scenario_result.status,
                scenario_result.elapsed
            )
        }

    def format_scenario_failed_event(self, scenario_result: ScenarioResult) -> Dict[str, Any]:
        return {
            "event": "scenario_failed",
            "timestamp": self._format_timestamp(time()),
            "scenario": self.format_scenario(
                scenario_result.scenario,
                scenario_result.status,
                scenario_result.elapsed
            )
        }

    def format_scenario_skipped_event(self, scenario_result: ScenarioResult) -> Dict[str, Any]:
        return {
            "event": "scenario_skipped",
            "timestamp": self._format_timestamp(time()),
            "scenario": self.format_scenario(
                scenario_result.scenario,
                scenario_result.status,
                scenario_result.elapsed
            )
        }

    def format_scenario_reported_event(self,
                                       aggregated_result: AggregatedResult) -> Dict[str, Any]:
        return {
            "event": "scenario_reported",
            "timestamp": self._format_timestamp(time()),
            "scenario": self.format_scenario(
                aggregated_result.scenario,
                aggregated_result.status,
                aggregated_result.elapsed
            ),
            "steps": self._format_steps(aggregated_result.step_results),
        }

    def format_cleanup_event(self, report: Any) -> Dict[str, Any]:
        return {
            "event": "cleanup",
            "timestamp": self._format_timestamp(time()),
            "report": {
                "total": report.total,
                "passed": report.passed,
                "failed": report.failed,
                "skipped": report.skipped,
                "elapsed": self._format_elapsed(report.elapsed),
                "interrupted": self.format_exc_info(report.interrupted),
            }
        }

    def format_scenario(self,
                        scenario: VirtualScenario,
                        status: ScenarioStatus,
                        elapsed: float
                        ) -> Dict[str, Any]:
        return {
            "id": scenario.unique_id,
            "subject": scenario.subject,
            "path": str(scenario.path),
            "lineno": scenario.lineno,
            "status": status.value,
            "elapsed": self._format_elapsed(elapsed),
            "skip_reason": scenario.skip_reason if scenario.is_skipped() else None,
        }

    def _format_steps(self, step_results: List[StepResult]) -> List[Dict[str, Any]]:
        steps = []
        for step_result in step_results:
            steps.append({
                "name": step_result.step.name,
                "status": step_result.status.value,
                "elapsed": self._format_elapsed(step_result.elapsed),
                "error": self.format_exc_info(step_result.exc_info),
            })
        return steps

    def _format_timestamp(self, timestamp: Union[float, None]) -> Union[int, None]:
        if timestamp is None:
            return None
        return int(timestamp * 1000)

    def _format_elapsed(self, elapsed: float) -> int:
        return int(elapsed * 1000)

    def format_exc_info(self, exc_info: Union[ExcInfo, None]) -> Union[Dict[str, Any], None]:
        if exc_info is None:
            return None

        file, lineno = None, None
        if exc_info.traceback is not None:
            file, lineno = self._get_traceback_lineno(exc_info.traceback)

        return {
            "type": exc_info.type.__name__,
            "message": str(exc_info.value),
            "file": file,
            "lineno": lineno,
        }

    def _get_traceback_lineno(self,
                              traceback: TracebackType
                              ) -> Tuple[Union[str, None], Union[int, None]]:
        tb = self._tb_filter.filter_tb(traceback)

        while tb.tb_next is not None:
            tb = tb.tb_next

        return tb.tb_frame.f_code.co_filename, tb.tb_lineno
