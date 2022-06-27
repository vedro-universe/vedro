from unittest.mock import Mock

import pytest

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


def make_scenario_result() -> ScenarioResult:
    vscenario = Mock(spec=VirtualScenario)
    return ScenarioResult(vscenario)
