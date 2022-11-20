import sys
from pathlib import Path
from time import monotonic_ns
from typing import Any, Callable, List, Optional

import pytest

from vedro import Scenario
from vedro.core import (
    AggregatedResult,
    Dispatcher,
    MonotonicScenarioRunner,
    ScenarioResult,
    VirtualScenario,
    VirtualStep,
)

if sys.version_info >= (3, 8):
    from unittest.mock import AsyncMock
else:
    from asynctest.mock import CoroutineMock as AsyncMock


__all__ = ("dispatcher_", "runner", "make_vstep", "make_vscenario", "make_aggregated_result",
           "AsyncMock",)


@pytest.fixture()
def dispatcher_():
    return AsyncMock(Dispatcher())


@pytest.fixture()
def runner(dispatcher_: Dispatcher):
    return MonotonicScenarioRunner(dispatcher_)


def make_vstep(callable: Callable[..., Any] = None, *, name: Optional[str] = None) -> VirtualStep:
    def step(self):
        if callable:
            callable(self)
    step.__name__ = name or f"step_{monotonic_ns()}"
    return VirtualStep(step)


def make_vscenario(steps: Optional[List[VirtualStep]] = None, *,
                   is_skipped: bool = False) -> VirtualScenario:
    class _Scenario(Scenario):
        __file__ = Path(f"scenario_{monotonic_ns()}.py").absolute()

    vsenario = VirtualScenario(_Scenario, steps=steps or [])
    if is_skipped:
        vsenario.skip()
    return vsenario


def make_scenario_result() -> ScenarioResult:
    return ScenarioResult(make_vscenario())


def make_aggregated_result(scenario_result: Optional[ScenarioResult] = None) -> AggregatedResult:
    if scenario_result is None:
        scenario_result = make_scenario_result()
    return AggregatedResult.from_existing(scenario_result, [scenario_result])
