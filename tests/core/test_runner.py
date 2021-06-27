import sys

from pytest import raises

if sys.version_info >= (3, 8):
    from unittest.mock import AsyncMock
else:
    from asynctest.mock import CoroutineMock as AsyncMock

from unittest.mock import Mock, call

import pytest
from baby_steps import given, then, when

from vedro import Scenario
from vedro._core import Dispatcher, Runner, VirtualScenario, VirtualStep
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


@pytest.mark.asyncio
@pytest.mark.parametrize("method_mock_factory", (Mock, AsyncMock,))
async def test_runner_run_step_passed(method_mock_factory: Mock, *,
                                      runner: Runner, dispatcher_: Dispatcher):
    with given:
        scenario_ = Mock(Scenario, step=method_mock_factory(return_value=None))
        step = VirtualStep(scenario_.step)

    with when:
        step_result = await runner.run_step(step, scenario_)

    with then:
        assert scenario_.mock_calls == [call.step(scenario_)]

        assert step_result.is_passed() is True
        assert step_result.exc_info is None
        assert isinstance(step_result.started_at, float)
        assert isinstance(step_result.ended_at, float)

        assert dispatcher_.mock_calls == [
            call.fire(StepRunEvent(step_result)),
            call.fire(StepPassedEvent(step_result)),
        ]


@pytest.mark.asyncio
@pytest.mark.parametrize("method_mock_factory", (Mock, AsyncMock))
async def test_runner_run_step_failed(method_mock_factory: Mock, *,
                                      runner: Runner, dispatcher_: Dispatcher):
    with given:
        exception = AssertionError()
        scenario_ = Mock(Scenario, step=method_mock_factory(side_effect=exception))
        step = VirtualStep(scenario_.step)

    with when:
        step_result = await runner.run_step(step, scenario_)

    with given:
        assert scenario_.mock_calls == [call.step(scenario_)]

        assert step_result.is_failed() is True

        assert step_result.exc_info.value == exception
        assert isinstance(step_result.started_at, float)
        assert isinstance(step_result.ended_at, float)

        assert dispatcher_.mock_calls == [
            call.fire(StepRunEvent(step_result)),
            call.fire(ExceptionRaisedEvent(step_result.exc_info)),
            call.fire(StepFailedEvent(step_result)),
        ]


@pytest.mark.asyncio
@pytest.mark.parametrize("method_mock_factory", (Mock, AsyncMock))
async def test_runner_run_step_interrupted(*, method_mock_factory: Mock, dispatcher_: Dispatcher):
    with given:
        interrupt_exception = KeyboardInterrupt
        scenario_ = Mock(Scenario, step=method_mock_factory(side_effect=interrupt_exception))
        virtual_step = VirtualStep(scenario_.step)

        runner = Runner(dispatcher_, interrupt_exceptions=(interrupt_exception,))

    with when, raises(BaseException) as exception:
        await runner.run_step(virtual_step, scenario_)

    with given:
        assert exception.type is interrupt_exception
        assert scenario_.mock_calls == [call.step(scenario_)]


@pytest.mark.asyncio
async def test_runner_run_scenario_no_steps_passed(*, runner: Runner, dispatcher_: Dispatcher):
    with given:
        scenario_ = Mock(Scenario, step=Mock(return_value=None), __file__="/tmp/scenario.py")
        virtual_scenario = VirtualScenario(scenario_, [])

    with when:
        scenario_result = await runner.run_scenario(virtual_scenario)

    with then:
        assert scenario_result.is_passed() is True
        assert isinstance(scenario_result.started_at, float)
        assert isinstance(scenario_result.ended_at, float)

        assert dispatcher_.mock_calls == [
            call.fire(ScenarioRunEvent(scenario_result)),
            call.fire(ScenarioPassedEvent(scenario_result)),
        ]


@pytest.mark.asyncio
async def test_runner_run_scenario_single_step_passed(*, runner: Runner, dispatcher_: Dispatcher):
    with given:
        scenario_ = Mock(Scenario, step=Mock(return_value=None), __file__="/tmp/scenario.py")
        step = VirtualStep(scenario_.step)
        virtual_scenario = VirtualScenario(scenario_, [step])

    with when:
        scenario_result = await runner.run_scenario(virtual_scenario)

    with then:
        assert scenario_result.is_passed() is True
        assert isinstance(scenario_result.started_at, float)
        assert isinstance(scenario_result.ended_at, float)

        step_results = scenario_result.step_results
        assert dispatcher_.mock_calls == [
            call.fire(ScenarioRunEvent(scenario_result)),
            call.fire(StepRunEvent(step_results[0])),
            call.fire(StepPassedEvent(step_results[0])),
            call.fire(ScenarioPassedEvent(scenario_result)),
        ]


@pytest.mark.asyncio
async def test_runner_run_scenario_single_step_failed(*, runner: Runner, dispatcher_: Dispatcher):
    with given:
        exception = AssertionError()
        scenario_ = Mock(Scenario, step=Mock(side_effect=exception), __file__="/tmp/scenario.py")

        step = VirtualStep(scenario_.step)
        virtual_scenario = VirtualScenario(scenario_, [step])

    with when:
        scenario_result = await runner.run_scenario(virtual_scenario)

    with then:
        assert scenario_result.is_failed() is True
        assert isinstance(scenario_result.started_at, float)
        assert isinstance(scenario_result.ended_at, float)

        step_results = scenario_result.step_results
        assert dispatcher_.mock_calls == [
            call.fire(ScenarioRunEvent(scenario_result)),
            call.fire(StepRunEvent(step_results[0])),
            call.fire(ExceptionRaisedEvent(step_results[0].exc_info)),
            call.fire(StepFailedEvent(step_results[0])),
            call.fire(ScenarioFailedEvent(scenario_result)),
        ]


@pytest.mark.asyncio
async def test_runner_run_scenario_multiple_steps_passed(*, runner: Runner,
                                                         dispatcher_: Dispatcher):
    with given:
        scenario_ = Mock(Scenario, __file__="/tmp/scenario.py",
                         first_step=Mock(return_value=None),
                         second_step=Mock(return_value=None))

        first_step = VirtualStep(scenario_.first_step)
        second_step = VirtualStep(scenario_.second_step)
        virtual_scenario = VirtualScenario(scenario_, [first_step, second_step])

    with when:
        scenario_result = await runner.run_scenario(virtual_scenario)

    with then:
        assert scenario_result.is_passed() is True
        assert isinstance(scenario_result.started_at, float)
        assert isinstance(scenario_result.ended_at, float)

        first_step_result = scenario_result.step_results[0]
        second_step_result = scenario_result.step_results[1]
        assert dispatcher_.mock_calls == [
            call.fire(ScenarioRunEvent(scenario_result)),

            call.fire(StepRunEvent(first_step_result)),
            call.fire(StepPassedEvent(first_step_result)),

            call.fire(StepRunEvent(second_step_result)),
            call.fire(StepPassedEvent(second_step_result)),

            call.fire(ScenarioPassedEvent(scenario_result)),
        ]


@pytest.mark.asyncio
async def test_runner_run_scenario_multiple_steps_failed():
    with given:
        dispatcher = AsyncMock(Dispatcher)
        runner = Runner(dispatcher)

        exception = AssertionError()
        scenario_ = Mock(Scenario, __file__="/tmp/scenario.py",
                         first_step=Mock(return_value=None),
                         second_step=Mock(side_effect=exception),
                         third_step=Mock(return_value=None))

        first_step = VirtualStep(scenario_.first_step)
        second_step = VirtualStep(scenario_.second_step)
        third_step = VirtualStep(scenario_.third_step)
        scenario = VirtualScenario(scenario_, [first_step, second_step, third_step])

    with when:
        scenario_result = await runner.run_scenario(scenario)

    with then:
        assert scenario_result.is_failed() is True
        assert isinstance(scenario_result.started_at, float)
        assert isinstance(scenario_result.ended_at, float)

        first_step_result = scenario_result.step_results[0]
        second_step_result = scenario_result.step_results[1]
        assert dispatcher.mock_calls == [
            call.fire(ScenarioRunEvent(scenario_result)),

            call.fire(StepRunEvent(first_step_result)),
            call.fire(StepPassedEvent(first_step_result)),

            call.fire(StepRunEvent(second_step_result)),
            call.fire(ExceptionRaisedEvent(second_step_result.exc_info)),
            call.fire(StepFailedEvent(second_step_result)),

            call.fire(ScenarioFailedEvent(scenario_result)),
        ]


@pytest.mark.asyncio
async def test_runner_interrupted_scenario(*, dispatcher_: Dispatcher):
    with given:
        interrupt_exception = KeyboardInterrupt
        runner = Runner(dispatcher_, interrupt_exceptions=(interrupt_exception,))

        step_ = Mock(side_effect=interrupt_exception)
        scenario_ = Mock(Scenario, step=step_, __file__="/tmp/scenario.py")
        virtual_scenario = VirtualScenario(scenario_, [VirtualStep(step_)])

    with when, raises(BaseException) as exception:
        await runner.run_scenario(virtual_scenario)

    with then:
        assert exception.type is interrupt_exception
