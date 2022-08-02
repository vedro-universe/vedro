from types import GeneratorType
from typing import Callable, Iterator, List

import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro.core import ScenarioResult, ScenarioScheduler, VirtualScenario

from ._utils import make_vscenario


class _ScenarioScheduler(ScenarioScheduler):
    @property
    def scheduled(self) -> Iterator[VirtualScenario]:
        yield from self.discovered

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


@pytest.mark.parametrize("get_scenarios", [
    lambda: [],
    lambda: [make_vscenario(), make_vscenario()]
])
def test_get_discovered(get_scenarios: Callable[[], List[VirtualScenario]]):
    with given:
        scenarios = get_scenarios()
        scheduler = _ScenarioScheduler(scenarios)

    with when:
        result = scheduler.discovered

    with then:
        assert isinstance(result, GeneratorType)
        assert list(result) == scenarios


@pytest.mark.parametrize("get_scenarios", [
    lambda: [],
    lambda: [make_vscenario(), make_vscenario()]
])
def test_get_scheduled(get_scenarios: Callable[[], List[VirtualScenario]]):
    with given:
        scenarios = get_scenarios()
        scheduler = _ScenarioScheduler(scenarios)

    with when:
        result = scheduler.scheduled

    with then:
        assert isinstance(result, GeneratorType)
        assert list(result) == scenarios
