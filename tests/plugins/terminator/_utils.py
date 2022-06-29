from pathlib import Path
from time import monotonic_ns

import pytest

from vedro import Scenario
from vedro.core import Dispatcher, ScenarioResult, VirtualScenario
from vedro.plugins.terminator import Terminator, TerminatorPlugin


@pytest.fixture()
def dispatcher() -> Dispatcher:
    return Dispatcher()


@pytest.fixture()
def terminator(dispatcher: Dispatcher) -> TerminatorPlugin:
    terminator = TerminatorPlugin(Terminator)
    terminator.subscribe(dispatcher)
    return terminator


def make_vscenario() -> VirtualScenario:
    class _Scenario(Scenario):
        __file__ = Path(f"scenario_{monotonic_ns()}.py").absolute()

    return VirtualScenario(_Scenario, steps=[])


def make_scenario_result() -> ScenarioResult:
    return ScenarioResult(make_vscenario())
