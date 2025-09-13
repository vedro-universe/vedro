from unittest.mock import Mock, call

import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro import Scenario
from vedro.core import MonotonicScenarioRunner as ScenarioRunner
from vedro.core import StepResult, VirtualStep
from vedro.core.output_capturer import OutputCapturer
from vedro.core.scenario_runner import StepInterrupted
from vedro.plugins.functioner._step_recorder import StepRecorder

from ._utils import AsyncMock, dispatcher_, interrupt_exception, runner, step_recorder

__all__ = ("dispatcher_", "runner", "interrupt_exception", "step_recorder",)  # fixtures


@pytest.mark.parametrize("method_mock_factory", (Mock, AsyncMock,))
async def test_fn_step_passed_no_recordings(method_mock_factory: Mock, *,
                                            runner: ScenarioRunner,
                                            dispatcher_: Mock,
                                            step_recorder: StepRecorder):
    with given:
        step_ = method_mock_factory(return_value=None, __name__="step")
        scenario_ = Mock(Scenario, step=step_)
        vstep = VirtualStep(step_)

    with when:
        step_result = await runner._run_fn_step(vstep, scenario_)

    with then("step_result created"):
        assert step_result.is_passed() is True
        assert step_result.exc_info is None
        assert isinstance(step_result.started_at, float)
        assert isinstance(step_result.ended_at, float)
        assert step_result.captured_output is None

    with then("step called"):
        assert step_.mock_calls == [call(scenario_)]

    with then("step_recorder cleared"):
        assert len(step_recorder) == 0


@pytest.mark.parametrize("method_mock_factory", (Mock, AsyncMock))
async def test_fn_step_failed_no_recordings(method_mock_factory: Mock, *,
                                            runner: ScenarioRunner,
                                            dispatcher_: Mock,
                                            step_recorder: StepRecorder):
    with given:
        exception = AssertionError()
        step_ = method_mock_factory(side_effect=exception, __name__="step")
        scenario_ = Mock(Scenario, step=step_)
        vstep = VirtualStep(step_)

    with when:
        step_result = await runner._run_fn_step(vstep, scenario_)

    with then("step_result created"):
        assert step_result.is_failed() is True
        assert step_result.exc_info.value == exception
        assert isinstance(step_result.started_at, float)
        assert isinstance(step_result.ended_at, float)
        assert step_result.captured_output is None

    with then("step called"):
        assert step_.mock_calls == [call(scenario_)]

    with then("step_recorder cleared"):
        assert len(step_recorder) == 0


@pytest.mark.parametrize("method_mock_factory", (Mock, AsyncMock))
async def test_fn_step_interrupted(method_mock_factory: Mock,
                                   dispatcher_: Mock,
                                   step_recorder: StepRecorder):
    with given:
        interrupt_exception = KeyboardInterrupt()
        step_ = method_mock_factory(side_effect=interrupt_exception, __name__="step")
        scenario_ = Mock(Scenario, step=step_)
        vstep = VirtualStep(step_)

        runner = ScenarioRunner(dispatcher_,
                                interrupt_exceptions=(interrupt_exception.__class__,),
                                step_recorder=step_recorder)

    with when, raises(BaseException) as exc:
        await runner._run_fn_step(vstep, scenario_)

    with then("exception raised"):
        assert exc.type is StepInterrupted

        orig_exc = exc.value
        assert orig_exc.exc_info.value == interrupt_exception
        assert isinstance(orig_exc.step_result, StepResult)

    with then("step_result created"):
        step_result = orig_exc.step_result
        assert step_result.is_failed()
        assert step_result.exc_info.value == orig_exc.exc_info.value
        assert isinstance(step_result.started_at, float)
        assert isinstance(step_result.ended_at, float)

    with then("step called"):
        assert step_.mock_calls == [call(scenario_)]

    with then("step_recorder cleared"):
        assert len(step_recorder) == 0


@pytest.mark.parametrize("method_mock_factory", (Mock, AsyncMock,))
async def test_fn_step_with_recordings(method_mock_factory: Mock, *,
                                       runner: ScenarioRunner,
                                       dispatcher_: Mock,
                                       step_recorder: StepRecorder):
    with given:
        def step_func(self):
            step_recorder.record("Given", "setup data", 1.0, 2.0)
            step_recorder.record("When", "perform action", 2.0, 3.0)
            step_recorder.record("Then", "verify result", 3.0, 4.0)

        step_ = method_mock_factory(side_effect=step_func, __name__="step")
        scenario_ = Mock(Scenario, step=step_)
        vstep = VirtualStep(step_)

    with when:
        step_result = await runner._run_fn_step(vstep, scenario_)

    with then("step_result created"):
        assert step_result.is_passed() is True
        assert step_result.exc_info is None
        assert isinstance(step_result.started_at, float)
        assert isinstance(step_result.ended_at, float)

    with then("step called"):
        assert step_.mock_calls == [call(scenario_)]

    with then("step_recorder has records"):
        assert list(step_recorder) == [
            ("Given", "setup data", 1.0, 2.0, None),
            ("When", "perform action", 2.0, 3.0, None),
            ("Then", "verify result", 3.0, 4.0, None),
        ]


@pytest.mark.parametrize("method_mock_factory", (Mock, AsyncMock,))
async def test_fn_step_with_recording_and_exception(method_mock_factory: Mock, *,
                                                    runner: ScenarioRunner,
                                                    dispatcher_: Mock,
                                                    step_recorder: StepRecorder):
    with given:
        exception = ValueError("test error")

        def step_func(self):
            step_recorder.record("Given", "setup data", 1.0, 2.0)
            step_recorder.record("When", "perform action", 2.0, 3.0, exc=exception)
            raise exception

        step_ = method_mock_factory(side_effect=step_func, __name__="step")
        scenario_ = Mock(Scenario, step=step_)
        vstep = VirtualStep(step_)

    with when:
        step_result = await runner._run_fn_step(vstep, scenario_)

    with then("step_result created"):
        assert step_result.is_failed() is True
        assert step_result.exc_info.value == exception
        assert isinstance(step_result.started_at, float)
        assert isinstance(step_result.ended_at, float)

    with then("step called"):
        assert step_.mock_calls == [call(scenario_)]

    with then("step_recorder has records"):
        assert list(step_recorder) == [
            ("Given", "setup data", 1.0, 2.0, None),
            ("When", "perform action", 2.0, 3.0, exception),
        ]


async def test_fn_step_with_captured_output(*,
                                            runner: ScenarioRunner,
                                            dispatcher_: Mock,
                                            step_recorder: StepRecorder):
    with given:
        test_output = "Test output from fn step"

        def step_func(self):
            print(test_output)
            step_recorder.record("Given", "print output", 1.0, 2.0)

        step_ = Mock(side_effect=step_func, __name__="step")
        scenario_ = Mock(Scenario, step=step_)
        vstep = VirtualStep(step_)

        output_capturer = OutputCapturer(enabled=True)

    with when:
        step_result = await runner._run_fn_step(
            vstep, scenario_, output_capturer=output_capturer
        )

    with then("step_result created with captured output"):
        assert step_result.is_passed() is True
        assert step_result.exc_info is None
        assert step_result.captured_output is not None
        assert test_output in step_result.captured_output.stdout.get_value()

    with then("step_recorder has records"):
        assert list(step_recorder) == [
            ("Given", "print output", 1.0, 2.0, None),
        ]
