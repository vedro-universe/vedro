import sys
from typing import Any, List, Type

if sys.version_info >= (3, 8):
    from unittest.mock import AsyncMock
else:
    from asynctest.mock import CoroutineMock as AsyncMock

from unittest.mock import Mock

import pytest
from baby_steps import given, then, when

from vedro import Scenario
from vedro.core import Dispatcher, Runner, VirtualScenario, VirtualStep
from vedro.events import (
    ExceptionRaisedEvent,
    ScenarioFailedEvent,
    ScenarioPassedEvent,
    ScenarioRunEvent,
    StepFailedEvent,
    StepPassedEvent,
    StepRunEvent,
)


@pytest.fixture()
def dispatcher_():
    return AsyncMock(Dispatcher())


@pytest.fixture()
def runner(dispatcher_: Dispatcher):
    return Runner(dispatcher_)


def assert_mock_calls(mock_calls: List[Any], expected: List[Any]) -> bool:
    assert len(mock_calls) == len(expected)

    for idx, exp in enumerate(expected):
        name, args, kwargs = mock_calls[idx]
        assert len(args) == 1
        assert isinstance(args[0], exp)

    return True


def make_scenario(steps: List[Any] = None) -> Type[Scenario]:
    kwargs = {}
    if steps is not None:
        for idx, step in enumerate(steps):
            kwargs[f"step_{idx}"] = step
    return Mock(Scenario, **kwargs, __file__="/tmp/scenario.py")


@pytest.mark.asyncio
@pytest.mark.parametrize("reruns", (0, 1))
async def test_runner_run_scenario(reruns: int, *, runner: Runner, dispatcher_: Dispatcher):
    with given:
        virtual_scenario = VirtualScenario(make_scenario(), [])

    with when:
        report = await runner.run([virtual_scenario], reruns=reruns)

    with then:
        assert report.total == report.passed == 1
        assert assert_mock_calls(dispatcher_.mock_calls, [
            ScenarioRunEvent,
            ScenarioPassedEvent,
        ])


@pytest.mark.asyncio
@pytest.mark.parametrize("reruns", (0, 1, 3))
async def test_runner_run_scenario_all_failed(reruns: int, *,
                                              runner: Runner, dispatcher_: Dispatcher):
    with given:
        step_ = Mock(side_effect=AssertionError())
        scenario_ = make_scenario(steps=[step_])

        step = VirtualStep(step_)
        virtual_scenario = VirtualScenario(scenario_, [step])

    with when:
        report = await runner.run([virtual_scenario], reruns=reruns)

    with then:
        assert report.total == report.failed == 1
        assert assert_mock_calls(dispatcher_.mock_calls, [
            ScenarioRunEvent,
            StepRunEvent,
            ExceptionRaisedEvent,
            StepFailedEvent,
            ScenarioFailedEvent,
        ] * (reruns + 1))


@pytest.mark.asyncio
async def test_runner_run_scenario_most_failed(runner: Runner, dispatcher_: Dispatcher):
    with given:
        step_ = Mock(side_effect=(AssertionError(), None, AssertionError()))
        scenario_ = make_scenario(steps=[step_])

        step = VirtualStep(step_)
        virtual_scenario = VirtualScenario(scenario_, [step])

    with when:
        report = await runner.run([virtual_scenario], reruns=2)

    with then:
        assert report.total == report.failed == 1
        assert assert_mock_calls(dispatcher_.mock_calls, [
            ScenarioRunEvent,
            StepRunEvent,
            ExceptionRaisedEvent,
            StepFailedEvent,
            ScenarioFailedEvent,

            ScenarioRunEvent,
            StepRunEvent,
            StepPassedEvent,
            ScenarioPassedEvent,

            ScenarioRunEvent,
            StepRunEvent,
            ExceptionRaisedEvent,
            StepFailedEvent,
            ScenarioFailedEvent,
        ])


@pytest.mark.asyncio
async def test_runner_run_scenario_most_passed(runner: Runner, dispatcher_: Dispatcher):
    with given:
        step_ = Mock(side_effect=(AssertionError(), None, None))
        scenario_ = make_scenario(steps=[step_])

        step = VirtualStep(step_)
        virtual_scenario = VirtualScenario(scenario_, [step])

    with when:
        report = await runner.run([virtual_scenario], reruns=2)

    with then:
        assert report.total == report.passed == 1
        assert assert_mock_calls(dispatcher_.mock_calls, [
            ScenarioRunEvent,
            StepRunEvent,
            ExceptionRaisedEvent,
            StepFailedEvent,
            ScenarioFailedEvent,

            ScenarioRunEvent,
            StepRunEvent,
            StepPassedEvent,
            ScenarioPassedEvent,

            ScenarioRunEvent,
            StepRunEvent,
            StepPassedEvent,
            ScenarioPassedEvent,
        ])
