"""
Test utilities for Vedro plugins.

This module provides helper functions to easily test Vedro plugins.

WARNING: This is an experimental module. The API and implementation can change
in any way without notice until it becomes stable. Use at your own risk in
production code.
"""

from pathlib import Path
from time import monotonic_ns
from typing import Optional

from vedro import Scenario
from vedro.core import (
    ScenarioResult,
    ScenarioStatus,
    StepResult,
    StepStatus,
    VirtualScenario,
    VirtualStep,
)

__all__ = ("make_vscenario", "make_scenario_result", "make_step_result",
           "make_passed_scenario_result", "make_failed_scenario_result",)


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


def make_failed_scenario_result(vscenario: Optional[VirtualScenario] = None, *,
                                started_at: Optional[float] = None,
                                ended_at: Optional[float] = None
                                ) -> ScenarioResult:
    return make_scenario_result(vscenario, status=ScenarioStatus.FAILED,
                                started_at=started_at, ended_at=ended_at)


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
