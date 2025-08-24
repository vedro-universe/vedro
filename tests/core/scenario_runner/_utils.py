from pathlib import Path
from time import monotonic_ns
from typing import Any, Callable, List, Optional, Type
from unittest.mock import AsyncMock

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

__all__ = ("dispatcher_", "runner", "interrupt_exception", "make_vstep", "make_vscenario",
           "make_scenario_result", "make_aggregated_result", "AsyncMock",)


@pytest.fixture()
def dispatcher_():
    return AsyncMock(Dispatcher())


@pytest.fixture()
def interrupt_exception():
    class InterruptException(KeyboardInterrupt):
        pass

    return InterruptException


@pytest.fixture()
def runner(dispatcher_: Dispatcher, interrupt_exception: Type[BaseException]):
    interrupt_exceptions = (interrupt_exception,)
    return MonotonicScenarioRunner(dispatcher_, interrupt_exceptions=interrupt_exceptions)


def make_vstep(callable: Callable[..., Any] = None, *, name: Optional[str] = None) -> VirtualStep:
    def step(self):
        if callable:
            callable(self)
    step.__name__ = name or f"step_{monotonic_ns()}"
    return VirtualStep(step)


def make_vscenario(steps: Optional[List[VirtualStep]] = None, *,
                   is_skipped: bool = False,
                   side_effect: Optional[Callable] = None) -> VirtualScenario:
    class _Scenario(Scenario):
        __file__ = Path(f"scenario_{monotonic_ns()}.py").absolute()

        if side_effect:
            def __init__(self):
                side_effect()

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
