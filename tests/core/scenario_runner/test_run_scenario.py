from os import linesep
from typing import Type, cast
from unittest.mock import Mock, call

import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro.core import Event, MonotonicScenarioRunner, ScenarioResult
from vedro.core.output_capturer import OutputCapturer
from vedro.core.scenario_runner import Interrupted, ScenarioInterrupted
from vedro.events import (
    ExceptionRaisedEvent,
    ScenarioFailedEvent,
    ScenarioPassedEvent,
    ScenarioRunEvent,
    ScenarioSkippedEvent,
    StepFailedEvent,
    StepPassedEvent,
    StepRunEvent,
)

from ._utils import (
    dispatcher_,
    interrupt_exception,
    make_vscenario,
    make_vstep,
    runner,
    step_recorder,
)

__all__ = ("dispatcher_", "runner", "interrupt_exception", "step_recorder",)  # fixtures


async def test_no_steps_passed(*, runner: MonotonicScenarioRunner, dispatcher_: Mock):
    with given:
        vscenario = make_vscenario(steps=[])

    with when:
        scenario_result = await runner.run_scenario(vscenario)

    with then("scenario_result created"):
        assert scenario_result.is_passed() is True
        assert isinstance(scenario_result.started_at, float)
        assert isinstance(scenario_result.ended_at, float)
        assert scenario_result.captured_output is None

    with then("events fired"):
        assert dispatcher_.mock_calls == [
            call.fire(ScenarioRunEvent(scenario_result)),
            call.fire(ScenarioPassedEvent(scenario_result)),
        ]


async def test_scenario_skipped(*, runner: MonotonicScenarioRunner, dispatcher_: Mock):
    with given:
        step_ = Mock()
        vstep = make_vstep(step_)
        vscenario = make_vscenario(steps=[vstep], is_skipped=True)

    with when:
        scenario_result = await runner.run_scenario(vscenario)

    with then("scenario_result created"):
        assert scenario_result.is_skipped() is True
        assert scenario_result.started_at is None
        assert scenario_result.ended_at is None
        assert scenario_result.captured_output is None

    with then("step not called"):
        assert step_.mock_calls == []

    with then("events fired"):
        assert dispatcher_.mock_calls == [
            call.fire(ScenarioSkippedEvent(scenario_result)),
        ]


async def test_single_step_passed(*, runner: MonotonicScenarioRunner, dispatcher_: Mock):
    with given:
        vstep = make_vstep()
        vscenario = make_vscenario(steps=[vstep])

    with when:
        scenario_result = await runner.run_scenario(vscenario)

    with then("scenario_result created"):
        assert scenario_result.is_passed() is True
        assert isinstance(scenario_result.started_at, float)
        assert isinstance(scenario_result.ended_at, float)
        assert scenario_result.captured_output is None

    with then("events fired"):
        step_result, = scenario_result.step_results
        assert dispatcher_.mock_calls == [
            call.fire(ScenarioRunEvent(scenario_result)),
            call.fire(StepRunEvent(step_result)),
            call.fire(StepPassedEvent(step_result)),
            call.fire(ScenarioPassedEvent(scenario_result)),
        ]


async def test_single_step_failed(*, runner: MonotonicScenarioRunner, dispatcher_: Mock):
    with given:
        exception = AssertionError()
        vstep = make_vstep(Mock(side_effect=exception))
        vscenario = make_vscenario(steps=[vstep])

    with when:
        scenario_result = await runner.run_scenario(vscenario)

    with then("scenario_result created"):
        assert scenario_result.is_failed() is True
        assert isinstance(scenario_result.started_at, float)
        assert isinstance(scenario_result.ended_at, float)
        assert scenario_result.captured_output is None

    with then("events fired"):
        step_result, = scenario_result.step_results
        assert dispatcher_.mock_calls == [
            call.fire(ScenarioRunEvent(scenario_result)),

            call.fire(StepRunEvent(step_result)),
            call.fire(ExceptionRaisedEvent(step_result.exc_info)),
            call.fire(StepFailedEvent(step_result)),

            call.fire(ScenarioFailedEvent(scenario_result)),
        ]


async def test_multiple_steps_passed(*, runner: MonotonicScenarioRunner, dispatcher_: Mock):
    with given:
        step1_, step2_ = Mock(return_value=None), Mock(return_value=None)
        vstep1, vstep2 = make_vstep(step1_), make_vstep(step2_)
        vscenario = make_vscenario(steps=[vstep1, vstep2])

    with when:
        scenario_result = await runner.run_scenario(vscenario)

    with then("scenario_result created"):
        assert scenario_result.is_passed() is True
        assert isinstance(scenario_result.started_at, float)
        assert isinstance(scenario_result.ended_at, float)

    with then("steps called"):
        assert step1_.assert_called_once() is None
        assert step2_.assert_called_once() is None

    with then("events fired"):
        step_result1, step_result2 = scenario_result.step_results
        assert dispatcher_.mock_calls == [
            call.fire(ScenarioRunEvent(scenario_result)),

            call.fire(StepRunEvent(step_result1)),
            call.fire(StepPassedEvent(step_result1)),

            call.fire(StepRunEvent(step_result2)),
            call.fire(StepPassedEvent(step_result2)),

            call.fire(ScenarioPassedEvent(scenario_result)),
        ]


async def test_multiple_steps_failed(*, runner: MonotonicScenarioRunner, dispatcher_: Mock):
    with given:
        exception = AssertionError()
        step1_, step2_ = Mock(side_effect=exception), Mock(side_effect=exception)
        vstep1, vstep2 = make_vstep(step1_), make_vstep(step2_)
        vscenario = make_vscenario(steps=[vstep1, vstep2])

    with when:
        scenario_result = await runner.run_scenario(vscenario)

    with then("scenario_result created"):
        assert scenario_result.is_failed() is True
        assert isinstance(scenario_result.started_at, float)
        assert isinstance(scenario_result.ended_at, float)

    with then("first step called"):
        assert step1_.assert_called_once() is None
        assert step2_.assert_not_called() is None

    with then("events fired"):
        step_result1 = scenario_result.step_results[0]
        assert dispatcher_.mock_calls == [
            call.fire(ScenarioRunEvent(scenario_result)),

            call.fire(StepRunEvent(step_result1)),
            call.fire(ExceptionRaisedEvent(step_result1.exc_info)),
            call.fire(StepFailedEvent(step_result1)),

            call.fire(ScenarioFailedEvent(scenario_result)),
        ]


@pytest.mark.parametrize("interrupt_exception", (KeyboardInterrupt, Interrupted))
async def test_step_interrupted(interrupt_exception: Type[BaseException], *, dispatcher_: Mock):
    with given:
        exception = interrupt_exception()
        step1_, step2_ = Mock(side_effect=exception), Mock(return_value=None)
        vstep1, vstep2 = make_vstep(step1_), make_vstep(step2_)
        vscenario = make_vscenario(steps=[vstep1, vstep2])

        runner = MonotonicScenarioRunner(dispatcher_, interrupt_exceptions=(interrupt_exception,))

    with when, raises(BaseException) as exc:
        await runner.run_scenario(vscenario)

    with then("exception raised"):
        assert exc.type is ScenarioInterrupted

        orig_exc = cast(ScenarioInterrupted, exc.value)
        assert isinstance(orig_exc.exc_info.value, interrupt_exception)
        assert isinstance(orig_exc.scenario_result, ScenarioResult)

    with then("scenario_result created"):
        scenario_result = orig_exc.scenario_result
        assert scenario_result.is_failed() is True
        assert isinstance(scenario_result.started_at, float)
        assert isinstance(scenario_result.ended_at, float)

    with then("first step called"):
        assert step1_.assert_called_once() is None
        assert step2_.assert_not_called() is None

    with then("events fired"):
        step_result, = orig_exc.scenario_result.step_results
        assert dispatcher_.mock_calls == [
            call.fire(ScenarioRunEvent(scenario_result)),

            call.fire(StepRunEvent(step_result)),
            call.fire(ExceptionRaisedEvent(orig_exc.exc_info)),
            call.fire(StepFailedEvent(step_result)),

            call.fire(ScenarioFailedEvent(scenario_result)),
        ]


async def test_scenario_interrupted(*, runner: MonotonicScenarioRunner,
                                    interrupt_exception: Type[BaseException], dispatcher_: Mock):
    with given:
        step1_, step2_ = Mock(), Mock()
        vstep1, vstep2 = make_vstep(step1_), make_vstep(step2_)
        vscenario = make_vscenario(steps=[vstep1, vstep2])

        async def fire(event: Event):
            if isinstance(event, StepPassedEvent):
                raise interrupt_exception()
            mock_calls.append(call.fire(type(event)))
        mock_calls = []
        dispatcher_.fire = fire

    with when, raises(BaseException) as exc:
        await runner.run_scenario(vscenario)

    with then("exception raised"):
        assert exc.type is ScenarioInterrupted

        orig_exc = cast(ScenarioInterrupted, exc.value)
        assert isinstance(orig_exc.exc_info.value, interrupt_exception)
        assert isinstance(orig_exc.scenario_result, ScenarioResult)

    with then("scenario_result created"):
        scenario_result = orig_exc.scenario_result
        assert scenario_result.is_failed() is True
        assert isinstance(scenario_result.started_at, float)
        assert isinstance(scenario_result.ended_at, float)
        assert len(scenario_result.step_results) == 0

    with then("first step called"):
        assert step1_.assert_called_once() is None
        assert step2_.assert_not_called() is None

    with then("events fired"):
        assert mock_calls == [
            call.fire(ScenarioRunEvent),
            call.fire(StepRunEvent),
            call.fire(ScenarioFailedEvent),
        ]


async def test_scenario_passed_with_captured_output(*, runner: MonotonicScenarioRunner,
                                                    dispatcher_: Mock):
    with given:
        test_output = "Test output from scenario initialization"

        # Create a side effect function that prints output
        def scenario_side_effect():
            print(test_output)

        vstep = make_vstep()
        vscenario = make_vscenario(steps=[vstep], side_effect=scenario_side_effect)

        output_capturer = OutputCapturer(enabled=True)

    with when:
        scenario_result = await runner.run_scenario(vscenario, output_capturer=output_capturer)

    with then("scenario_result created with captured output"):
        assert scenario_result.is_passed() is True
        assert isinstance(scenario_result.started_at, float)
        assert isinstance(scenario_result.ended_at, float)

        assert scenario_result.captured_output is not None
        assert scenario_result.captured_output.stdout.get_value() == f"{test_output}{linesep}"


async def test_scenario_skipped_with_captured_output(*, runner: MonotonicScenarioRunner,
                                                     dispatcher_: Mock):
    with given:
        test_output = "Test output from skipped scenario initialization"

        # Create a side effect function that prints output
        def scenario_side_effect():
            print(test_output)

        vscenario = make_vscenario(steps=[], is_skipped=True, side_effect=scenario_side_effect)

        # Create output capturer with capturing enabled
        output_capturer = OutputCapturer(enabled=True)

    with when:
        scenario_result = await runner.run_scenario(vscenario, output_capturer=output_capturer)

    with then("scenario_result created without captured output"):
        assert scenario_result.is_skipped() is True
        assert scenario_result.started_at is None
        assert scenario_result.ended_at is None

        # Skipped scenarios don't initialize or run, so no output is captured
        assert scenario_result.captured_output is None
