"""
Test utilities for Vedro plugins.

This module provides helper functions to easily test Vedro plugins.

WARNING: This is an experimental module. The API and implementation can change
in any way without notice until it becomes stable. Use at your own risk in
production code.
"""

from pathlib import Path
from time import monotonic_ns
from typing import List, Optional

from vedro import Scenario
from vedro.core import (
    AggregatedResult,
    Dispatcher,
    Report,
    ScenarioResult,
    ScenarioStatus,
    StepResult,
    StepStatus,
    VirtualScenario,
    VirtualStep,
)
from vedro.core.scenario_scheduler import MonotonicScenarioScheduler, ScenarioScheduler
from vedro.events import (
    CleanupEvent,
    ScenarioFailedEvent,
    ScenarioPassedEvent,
    ScenarioReportedEvent,
    ScenarioRunEvent,
    ScenarioSkippedEvent,
    StartupEvent,
)

__all__ = ("make_vscenario", "make_scenario_result", "make_step_result",
           "make_passed_scenario_result", "make_failed_scenario_result",
           "make_passed_step_result", "make_failed_step_result",
           "make_skipped_scenario_result", "make_aggregated_result",
           "make_dispatcher", "make_scenario_scheduler",
           "make_startup_event", "make_scenario_run_event",
           "make_scenario_passed_event", "make_scenario_failed_event",
           "make_scenario_skipped_event", "make_scenario_reported_event",
           "make_cleanup_event",)


def make_vscenario() -> VirtualScenario:
    class _Scenario(Scenario):
        __file__ = Path(f"scenario_{monotonic_ns()}.py").absolute()

    return VirtualScenario(_Scenario, steps=[])


def make_scenario_result(vscenario: Optional[VirtualScenario] = None, *,
                         status: ScenarioStatus = ScenarioStatus.PENDING,
                         started_at: Optional[float] = None,
                         ended_at: Optional[float] = None
                         ) -> ScenarioResult:
    if vscenario is None:
        vscenario = make_vscenario()

    scenario_result = ScenarioResult(vscenario)

    if status is ScenarioStatus.PASSED:
        scenario_result.mark_passed()
    elif status is ScenarioStatus.FAILED:
        scenario_result.mark_failed()
    elif status is ScenarioStatus.SKIPPED:
        scenario_result.mark_skipped()

    if started_at is not None:
        scenario_result.set_started_at(started_at)

    if ended_at is not None:
        scenario_result.set_ended_at(ended_at)

    return scenario_result


def make_passed_scenario_result(vscenario: Optional[VirtualScenario] = None, *,
                                started_at: Optional[float] = None,
                                ended_at: Optional[float] = None
                                ) -> ScenarioResult:
    return make_scenario_result(vscenario, status=ScenarioStatus.PASSED,
                                started_at=started_at, ended_at=ended_at)


# step_results: list[StepResult] = []
def make_failed_scenario_result(vscenario: Optional[VirtualScenario] = None, *,
                                started_at: Optional[float] = None,
                                ended_at: Optional[float] = None
                                ) -> ScenarioResult:
    return make_scenario_result(vscenario, status=ScenarioStatus.FAILED,
                                started_at=started_at, ended_at=ended_at)


def make_skipped_scenario_result(vscenario: Optional[VirtualScenario] = None, *,
                                 started_at: Optional[float] = None,
                                 ended_at: Optional[float] = None
                                 ) -> ScenarioResult:
    if vscenario is None:
        vscenario = make_vscenario()
        vscenario.skip()
    return make_scenario_result(vscenario, status=ScenarioStatus.SKIPPED,
                                started_at=started_at, ended_at=ended_at)


# list
def make_aggregated_result(scenario_result: Optional[ScenarioResult] = None) -> AggregatedResult:
    if scenario_result is None:
        scenario_result = make_scenario_result()
    return AggregatedResult.from_existing(scenario_result, [scenario_result])


def make_step_result(vstep: Optional[VirtualStep] = None, *,
                     status: StepStatus = StepStatus.PENDING,
                     started_at: Optional[float] = None,
                     ended_at: Optional[float] = None
                     ) -> StepResult:
    if vstep is None:
        def do() -> None:
            pass
        vstep = VirtualStep(do)

    step_result = StepResult(vstep)

    if status is StepStatus.PASSED:
        step_result.mark_passed()
    elif status is StepStatus.FAILED:
        step_result.mark_failed()

    if started_at is not None:
        step_result.set_started_at(started_at)

    if ended_at is not None:
        step_result.set_ended_at(ended_at)

    return step_result


def make_passed_step_result(vstep: Optional[VirtualStep] = None, *,
                            started_at: Optional[float] = None,
                            ended_at: Optional[float] = None
                            ) -> StepResult:
    return make_step_result(vstep, status=StepStatus.PASSED,
                            started_at=started_at, ended_at=ended_at)


def make_failed_step_result(vstep: Optional[VirtualStep] = None, *,
                            started_at: Optional[float] = None,
                            ended_at: Optional[float] = None
                            ) -> StepResult:
    return make_step_result(vstep, status=StepStatus.FAILED,
                            started_at=started_at, ended_at=ended_at)


def make_dispatcher() -> Dispatcher:
    return Dispatcher()


def make_scenario_scheduler(scenarios: Optional[List[VirtualScenario]] = None
                            ) -> ScenarioScheduler:
    if scenarios is None:
        scenarios = []
    return MonotonicScenarioScheduler(scenarios=scenarios)


def make_startup_event(scheduler: Optional[ScenarioScheduler] = None) -> StartupEvent:
    if scheduler is None:
        scheduler = make_scenario_scheduler()
    return StartupEvent(scheduler)


def make_scenario_run_event(scenario_result: Optional[ScenarioResult] = None
                            ) -> ScenarioRunEvent:
    if scenario_result is None:
        scenario_result = make_scenario_result()
    return ScenarioRunEvent(scenario_result)


def make_scenario_passed_event(scenario_result: Optional[ScenarioResult] = None
                               ) -> ScenarioPassedEvent:
    if scenario_result is None:
        scenario_result = make_passed_scenario_result()
    return ScenarioPassedEvent(scenario_result)


def make_scenario_failed_event(scenario_result: Optional[ScenarioResult] = None
                               ) -> ScenarioFailedEvent:
    if scenario_result is None:
        scenario_result = make_failed_scenario_result()
    return ScenarioFailedEvent(scenario_result)


def make_scenario_skipped_event(scenario_result: Optional[ScenarioResult] = None
                                ) -> ScenarioSkippedEvent:
    if scenario_result is None:
        scenario_result = make_skipped_scenario_result()
    return ScenarioSkippedEvent(scenario_result)


def make_scenario_reported_event(aggregated_result: Optional[AggregatedResult] = None
                                 ) -> ScenarioReportedEvent:
    if aggregated_result is None:
        aggregated_result = make_aggregated_result()
    return ScenarioReportedEvent(aggregated_result)


def make_cleanup_event(report: Optional[Report] = None) -> CleanupEvent:
    if report is None:
        report = Report()
    return CleanupEvent(report)
