from types import GeneratorType
from typing import List
from unittest.mock import Mock

import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro.core import ScenarioResult, ScenarioScheduler, VirtualScenario


class _ScenarioScheduler(ScenarioScheduler):
    def schedule(self, scenario: VirtualScenario) -> None:
        pass

    def ignore(self, scenario: VirtualScenario) -> None:
        pass

    def aggregate_results(self, scenario_results: List[ScenarioResult]) -> ScenarioResult:
        pass

    async def __anext__(self) -> VirtualScenario:
        raise StopAsyncIteration()


def make_virtual_scenario() -> Mock:
    return Mock(spec=VirtualScenario)


def test_abstract():
    with when, raises(BaseException) as exc:
        ScenarioScheduler([])

    with then:
        assert exc.type is TypeError


@pytest.mark.parametrize("scenarios", [
    [],
    [make_virtual_scenario(), make_virtual_scenario()]
])
def test_get_scenarios(scenarios):
    with given:
        scheduler = _ScenarioScheduler(scenarios)

    with when:
        result = scheduler.scenarios

    with then:
        assert isinstance(result, GeneratorType)
        assert list(result) == scenarios
