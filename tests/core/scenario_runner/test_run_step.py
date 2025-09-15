from os import linesep
from typing import Type, cast
from unittest.mock import Mock, call

import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro import Scenario
from vedro.core import MonotonicScenarioRunner, StepResult, VirtualStep
from vedro.core.output_capturer import OutputCapturer
from vedro.core.scenario_runner import Interrupted, StepInterrupted
from vedro.events import ExceptionRaisedEvent, StepFailedEvent, StepPassedEvent, StepRunEvent

from ._utils import AsyncMock, dispatcher_, interrupt_exception, runner, step_recorder

__all__ = ("dispatcher_", "runner", "interrupt_exception", "step_recorder",)  # fixtures


@pytest.mark.parametrize("method_mock_factory", (Mock, AsyncMock,))
async def test_step_passed(method_mock_factory: Mock, *,
                           runner: MonotonicScenarioRunner, dispatcher_: Mock):
    with given:
        step_ = method_mock_factory(return_value=None, __name__="step")
        scenario_ = Mock(Scenario, step=step_)
        vstep = VirtualStep(step_)

    with when:
        step_result = await runner.run_step(vstep, scenario_)

    with then("step_result created"):
        assert step_result.is_passed() is True
        assert step_result.exc_info is None
        assert isinstance(step_result.started_at, float)
        assert isinstance(step_result.ended_at, float)
        assert step_result.captured_output is None

    with then("step called"):
        assert step_.mock_calls == [call(scenario_)]

    with then("events fired"):
        assert dispatcher_.mock_calls == [
            call.fire(StepRunEvent(step_result)),
            call.fire(StepPassedEvent(step_result)),
        ]


@pytest.mark.parametrize("method_mock_factory", (Mock, AsyncMock))
async def test_step_failed(method_mock_factory: Mock, *,
                           runner: MonotonicScenarioRunner, dispatcher_: Mock):
    with given:
        exception = AssertionError()
        step_ = method_mock_factory(side_effect=exception, __name__="step")
        scenario_ = Mock(Scenario, step=step_)
        vstep = VirtualStep(step_)

    with when:
        step_result = await runner.run_step(vstep, scenario_)

    with then("step_result created"):
        assert step_result.is_failed() is True
        assert step_result.exc_info.value == exception
        assert isinstance(step_result.started_at, float)
        assert isinstance(step_result.ended_at, float)
        assert step_result.captured_output is None

    with then("step called"):
        assert step_.mock_calls == [call(scenario_)]

    with then("events fired"):
        assert dispatcher_.mock_calls == [
            call.fire(StepRunEvent(step_result)),
            call.fire(ExceptionRaisedEvent(step_result.exc_info)),
            call.fire(StepFailedEvent(step_result)),
        ]


@pytest.mark.parametrize("method_mock_factory", (Mock, AsyncMock))
@pytest.mark.parametrize("interrupt_exception", (KeyboardInterrupt, Interrupted))
async def test_step_interrupted(method_mock_factory: Mock, interrupt_exception: Type[Exception], *,
                                dispatcher_: Mock):
    with given:
        exception = interrupt_exception()
        step_ = method_mock_factory(side_effect=exception, __name__="step")
        scenario_ = Mock(Scenario, step=step_)
        vstep = VirtualStep(step_)

        runner = MonotonicScenarioRunner(dispatcher_, interrupt_exceptions=(interrupt_exception,))

    with when, raises(BaseException) as exc:
        await runner.run_step(vstep, scenario_)

    with then("exception raised"):
        assert exc.type is StepInterrupted

        orig_exc = cast(StepInterrupted, exc.value)
        assert orig_exc.exc_info.value == exception
        assert isinstance(orig_exc.step_result, StepResult)

    with then("step_result created"):
        step_result = orig_exc.step_result
        assert step_result.is_failed()
        assert step_result.exc_info.value == orig_exc.exc_info.value
        assert isinstance(step_result.started_at, float)
        assert isinstance(step_result.ended_at, float)
        assert step_result.captured_output is None

    with then("step called"):
        assert step_.mock_calls == [call(scenario_)]

    with then("events fired"):
        assert dispatcher_.mock_calls == [
            call.fire(StepRunEvent(step_result)),
            call.fire(ExceptionRaisedEvent(step_result.exc_info)),
            call.fire(StepFailedEvent(step_result)),
        ]


@pytest.mark.parametrize("method_mock_factory", (Mock, AsyncMock,))
async def test_step_passed_with_captured_output(method_mock_factory: Mock, *,
                                                runner: MonotonicScenarioRunner,
                                                dispatcher_: Mock):
    with given:
        test_output = "Test output from step"

        # Create a step function that prints output
        def step_func(self):
            print(test_output)

        step_ = method_mock_factory(side_effect=step_func, __name__="step")
        scenario_ = Mock(Scenario, step=step_)
        vstep = VirtualStep(step_)

        output_capturer = OutputCapturer(enabled=True)

    with when:
        step_result = await runner.run_step(vstep, scenario_, output_capturer=output_capturer)

    with then("step_result created with captured output"):
        assert step_result.is_passed() is True
        assert step_result.exc_info is None
        assert isinstance(step_result.started_at, float)
        assert isinstance(step_result.ended_at, float)

        assert step_result.captured_output is not None
        assert step_result.captured_output.stdout.get_value() == f"{test_output}{linesep}"


@pytest.mark.parametrize("method_mock_factory", (Mock, AsyncMock,))
async def test_step_failed_with_captured_output(method_mock_factory: Mock, *,
                                                runner: MonotonicScenarioRunner,
                                                dispatcher_: Mock):
    with given:
        test_output = "Test output from failing step"

        # Create a step function that prints output and then fails
        def step_func(self):
            print(test_output)
            raise AssertionError("Step failed after printing")

        step_ = method_mock_factory(side_effect=step_func, __name__="step")
        scenario_ = Mock(Scenario, step=step_)
        vstep = VirtualStep(step_)

        output_capturer = OutputCapturer(enabled=True)

    with when:
        step_result = await runner.run_step(vstep, scenario_, output_capturer=output_capturer)

    with then("step_result created with captured output"):
        assert step_result.is_failed() is True
        assert step_result.exc_info is not None
        assert isinstance(step_result.exc_info.value, AssertionError)
        assert str(step_result.exc_info.value) == "Step failed after printing"
        assert isinstance(step_result.started_at, float)
        assert isinstance(step_result.ended_at, float)

        assert step_result.captured_output is not None
        assert step_result.captured_output.stdout.get_value() == f"{test_output}{linesep}"


@pytest.mark.parametrize("method_mock_factory", (Mock, AsyncMock))
@pytest.mark.parametrize("interrupt_exception", (KeyboardInterrupt, Interrupted))
async def test_step_interrupted_with_captured_output(method_mock_factory: Mock,
                                                     interrupt_exception: Type[Exception], *,
                                                     dispatcher_: Mock):
    with given:
        test_output = "Test output from interrupted step"

        # Create a step function that prints output and then is interrupted
        def step_func(self):
            print(test_output)
            raise interrupt_exception()

        step_ = method_mock_factory(side_effect=step_func, __name__="step")
        scenario_ = Mock(Scenario, step=step_)
        vstep = VirtualStep(step_)

        output_capturer = OutputCapturer(enabled=True)

        runner = MonotonicScenarioRunner(dispatcher_, interrupt_exceptions=(interrupt_exception,))

    with when, raises(BaseException) as exc:
        await runner.run_step(vstep, scenario_, output_capturer=output_capturer)

    with then("exception raised"):
        assert exc.type is StepInterrupted

        orig_exc = cast(StepInterrupted, exc.value)
        assert isinstance(orig_exc.exc_info.value, interrupt_exception)
        assert isinstance(orig_exc.step_result, StepResult)

    with then("step_result created with captured output"):
        step_result = orig_exc.step_result
        assert step_result.is_failed()
        assert step_result.exc_info.value == orig_exc.exc_info.value
        assert isinstance(step_result.started_at, float)
        assert isinstance(step_result.ended_at, float)

        assert step_result.captured_output is not None
        assert step_result.captured_output.stdout.get_value() == f"{test_output}{linesep}"
