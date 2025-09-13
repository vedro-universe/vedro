from os import linesep
from unittest.mock import Mock, call

from baby_steps import given, then, when

from vedro.core import ExcInfo
from vedro.core import MonotonicScenarioRunner as ScenarioRunner
from vedro.core import ScenarioResult, StepResult, VirtualStep
from vedro.core.output_capturer import CapturedOutput
from vedro.events import (
    ExceptionRaisedEvent,
    ScenarioFailedEvent,
    ScenarioPassedEvent,
    StepFailedEvent,
    StepPassedEvent,
    StepRunEvent,
)
from vedro.plugins.functioner._step_recorder import StepRecorder

from ._utils import dispatcher_, interrupt_exception, make_vscenario, runner, step_recorder

__all__ = ("dispatcher_", "interrupt_exception", "runner", "step_recorder",)


async def test_no_recorded_steps_passed(*, runner: ScenarioRunner,
                                        step_recorder: StepRecorder,
                                        dispatcher_: Mock):
    with given:
        step_ = Mock(return_value=None, __name__="step")
        vstep = VirtualStep(step_)
        step_result = StepResult(vstep)
        step_result.set_started_at(1.0).set_ended_at(2.0).mark_passed()

        vscenario = make_vscenario()
        scenario_result = ScenarioResult(vscenario)
        scenario_result.set_started_at(1.0)

    with when:
        await runner._fire_fn_step_events(step_result, scenario_result)

    with then("events fired for single step"):
        assert dispatcher_.mock_calls == [
            call.fire(StepRunEvent(step_result)),
            call.fire(StepPassedEvent(step_result)),
            call.fire(ScenarioPassedEvent(scenario_result)),
        ]

    with then("scenario result updated"):
        assert scenario_result.is_passed()
        assert len(scenario_result.step_results) == 1
        assert scenario_result.step_results[0] == step_result
        assert isinstance(scenario_result.ended_at, float)


async def test_no_recorded_steps_failed(*, runner: ScenarioRunner,
                                        step_recorder: StepRecorder,
                                        dispatcher_: Mock):
    with given:
        exception = ValueError("test error")
        exc_info = ExcInfo(ValueError, exception, None)

        step_ = Mock(side_effect=exception, __name__="step")
        vstep = VirtualStep(step_)
        step_result = StepResult(vstep)
        step_result.set_started_at(1.0).set_ended_at(2.0).mark_failed()
        step_result.set_exc_info(exc_info)

        vscenario = make_vscenario()
        scenario_result = ScenarioResult(vscenario)
        scenario_result.set_started_at(1.0)

    with when:
        await runner._fire_fn_step_events(step_result, scenario_result)

    with then("events fired for failed step"):
        assert dispatcher_.mock_calls == [
            call.fire(StepRunEvent(step_result)),
            call.fire(ExceptionRaisedEvent(exc_info)),
            call.fire(StepFailedEvent(step_result)),
            call.fire(ScenarioFailedEvent(scenario_result)),
        ]

    with then("scenario result updated"):
        assert scenario_result.is_failed()
        assert len(scenario_result.step_results) == 1
        assert scenario_result.step_results[0] == step_result
        assert isinstance(scenario_result.ended_at, float)


async def test_recorded_steps_all_passing(*, runner: ScenarioRunner,
                                          step_recorder: StepRecorder,
                                          dispatcher_: Mock):
    with given:
        step_recorder.record("Given", "setup data", 1.0, 2.0)
        step_recorder.record("When", "perform action", 2.0, 3.0)
        step_recorder.record("Then", "verify result", 3.0, 4.0)

        # Include captured output to test that functionality too
        captured = CapturedOutput()
        with captured:
            print("test output")

        step_ = Mock(return_value=None, __name__="step")
        vstep = VirtualStep(step_)
        step_result = StepResult(vstep)
        step_result.set_started_at(1.0).set_ended_at(4.0).mark_passed()
        step_result.set_captured_output(captured)

        vscenario = make_vscenario()
        scenario_result = ScenarioResult(vscenario)
        scenario_result.set_started_at(1.0)

    with when:
        await runner._fire_fn_step_events(step_result, scenario_result)

    with then("scenario result has all step results"):
        assert scenario_result.is_passed()
        assert len(scenario_result.step_results) == 3

    with then("events fired for each recorded step"):
        step_result1, step_result2, step_result3 = scenario_result.step_results
        assert dispatcher_.mock_calls == [
            call.fire(StepRunEvent(step_result1)),
            call.fire(StepPassedEvent(step_result1)),

            call.fire(StepRunEvent(step_result2)),
            call.fire(StepPassedEvent(step_result2)),

            call.fire(StepRunEvent(step_result3)),
            call.fire(StepPassedEvent(step_result3)),

            call.fire(ScenarioPassedEvent(scenario_result)),
        ]

        assert step_result1.is_passed()
        assert step_result1.step.name == "given setup data"
        assert step_result1.started_at == 1.0
        assert step_result1.ended_at == 2.0

        assert step_result2.step.name == "when perform action"
        assert step_result2.is_passed()
        assert step_result2.started_at == 2.0
        assert step_result2.ended_at == 3.0

        assert step_result3.step.name == "then verify result"
        assert step_result3.is_passed()
        assert step_result3.started_at == 3.0
        assert step_result3.ended_at == 4.0

    with then("captured output transferred to scenario"):
        assert scenario_result.captured_output == captured
        assert scenario_result.captured_output.stdout.get_value() == f"test output{linesep}"


async def test_recorded_step_with_failure(*, runner: ScenarioRunner,
                                          step_recorder: StepRecorder,
                                          dispatcher_: Mock):
    with given:
        exception = AssertionError("test failure")
        exc_info = ExcInfo(AssertionError, exception, None)

        step_recorder.record("Given", "setup data", 1.0, 2.0)
        step_recorder.record("When", "perform action", 2.0, 3.0, exc=exception)
        # Note: no "Then" step because execution stopped at failure

        step_ = Mock(side_effect=exception, __name__="step")
        vstep = VirtualStep(step_)
        step_result = StepResult(vstep)
        step_result.set_started_at(1.0).set_ended_at(3.0).mark_failed()
        step_result.set_exc_info(exc_info)

        vscenario = make_vscenario()
        scenario_result = ScenarioResult(vscenario)
        scenario_result.set_started_at(1.0)

    with when:
        await runner._fire_fn_step_events(step_result, scenario_result)

    with then("scenario result has steps until failure"):
        assert scenario_result.is_failed()
        assert len(scenario_result.step_results) == 2

    with then("events fired until failure"):
        step_result1, step_result2 = scenario_result.step_results
        assert dispatcher_.mock_calls == [
            call.fire(StepRunEvent(step_result1)),
            call.fire(StepPassedEvent(step_result1)),

            call.fire(StepRunEvent(step_result2)),
            call.fire(ExceptionRaisedEvent(exc_info)),
            call.fire(StepFailedEvent(step_result2)),

            call.fire(ScenarioFailedEvent(scenario_result)),
        ]

        # First step passed
        assert step_result1.is_passed()
        assert step_result1.step.name == "given setup data"
        assert step_result1.started_at == 1.0
        assert step_result1.ended_at == 2.0

        # Second step failed
        assert step_result2.is_failed()
        assert step_result2.step.name == "when perform action"
        assert step_result2.started_at == 2.0
        assert step_result2.ended_at == 3.0
        assert step_result2.exc_info == exc_info


async def test_exception_outside_step_context(*, runner: ScenarioRunner,
                                              step_recorder: StepRecorder,
                                              dispatcher_: Mock):
    with given:
        exception = RuntimeError("exception outside steps")
        exc_info = ExcInfo(RuntimeError, exception, None)

        step_recorder.record("Given", "setup data", 1.0, 2.0)
        step_recorder.record("When", "perform action", 2.0, 3.0)
        # Exception happens after all steps completed

        step_ = Mock(side_effect=exception, __name__="step")
        vstep = VirtualStep(step_)
        step_result = StepResult(vstep)
        step_result.set_started_at(1.0).set_ended_at(4.0).mark_failed()
        step_result.set_exc_info(exc_info)

        vscenario = make_vscenario()
        scenario_result = ScenarioResult(vscenario)
        scenario_result.set_started_at(1.0)

    with when:
        await runner._fire_fn_step_events(step_result, scenario_result)

    with then("scenario result has synthetic error step"):
        assert scenario_result.is_failed()
        assert len(scenario_result.step_results) == 3

    with then("events include synthetic error step"):
        step_result1, step_result2, step_result3 = scenario_result.step_results
        assert dispatcher_.mock_calls == [
            call.fire(StepRunEvent(step_result1)),
            call.fire(StepPassedEvent(step_result1)),

            call.fire(StepRunEvent(step_result2)),
            call.fire(StepPassedEvent(step_result2)),

            call.fire(StepRunEvent(step_result3)),
            call.fire(ExceptionRaisedEvent(exc_info)),
            call.fire(StepFailedEvent(step_result3)),

            call.fire(ScenarioFailedEvent(scenario_result)),
        ]

        # First two steps passed
        assert step_result1.is_passed()
        assert step_result1.step.name == "given setup data"
        assert step_result1.started_at == 1.0
        assert step_result1.ended_at == 2.0

        assert step_result2.is_passed()
        assert step_result2.step.name == "when perform action"
        assert step_result2.started_at == 2.0
        assert step_result2.ended_at == 3.0

        # Synthetic error step failed
        assert step_result3.is_failed()
        assert step_result3.step.name == "unexpected_error"
        assert step_result3.exc_info == exc_info
