from pathlib import Path
from time import monotonic_ns

import pytest

from vedro import Scenario
from vedro.core import AggregatedResult, ScenarioResult, StepResult, VirtualScenario, VirtualStep


@pytest.fixture()
def aggregated_result() -> AggregatedResult:
    return AggregatedResult(make_vscenario())


def make_vscenario() -> VirtualScenario:
    class _Scenario(Scenario):
        __file__ = Path(f"scenario_{monotonic_ns()}.py").absolute()

    return VirtualScenario(_Scenario, steps=[])


def make_scenario_result() -> ScenarioResult:
    return ScenarioResult(make_vscenario())


def make_vstep() -> VirtualStep:
    return VirtualStep(lambda self: None)


def make_step_result() -> StepResult:
    return StepResult(make_vstep())
