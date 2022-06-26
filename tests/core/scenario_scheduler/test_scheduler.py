from types import GeneratorType
from typing import List

import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro.core import ScenarioResult, ScenarioScheduler, VirtualScenario

from ._utils import make_virtual_scenario


class _ScenarioScheduler(ScenarioScheduler):
    def schedule(self, scenario: VirtualScenario) -> None:
        pass

    def ignore(self, scenario: VirtualScenario) -> None:
        pass

    def aggregate_results(self, scenario_results: List[ScenarioResult]) -> ScenarioResult:
        pass

    async def __anext__(self) -> VirtualScenario:
        raise StopAsyncIteration()


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
