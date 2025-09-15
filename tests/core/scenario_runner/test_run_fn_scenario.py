from typing import Type, cast
from unittest.mock import Mock, call

from baby_steps import given, then, when
from pytest import raises

from vedro.core import MonotonicScenarioRunner, VirtualScenario
from vedro.core.scenario_runner import ScenarioInterrupted
from vedro.events import (
    ScenarioFailedEvent,
    ScenarioPassedEvent,
    ScenarioRunEvent,
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

__all__ = ("dispatcher_", "interrupt_exception", "runner", "step_recorder",)


def make_fn_scenario(step_callable=None, *, is_skipped: bool = False) -> VirtualScenario:
    vstep = make_vstep(step_callable or Mock(return_value=None))
    vscenario = make_vscenario(steps=[vstep], is_skipped=is_skipped)

    # Mark as function-based scenario
    vscenario._orig_scenario.__vedro__fn__ = True

    return vscenario


async def test_fn_scenario_success(*, runner: MonotonicScenarioRunner, dispatcher_: Mock):
    with given:
        step_mock = Mock(return_value=None)
        vscenario = make_fn_scenario(step_mock)

    with when:
        scenario_result = await runner.run_scenario(vscenario)

    with then("scenario passes"):
        assert scenario_result.is_passed()
        assert isinstance(scenario_result.started_at, float)
        assert isinstance(scenario_result.ended_at, float)

    with then("step was called"):
        step_mock.assert_called_once()

    with then("events include scenario and step passed events"):
        step_result = scenario_result.step_results[0]
        assert dispatcher_.mock_calls == [
            call.fire(ScenarioRunEvent(scenario_result)),
            call.fire(StepRunEvent(step_result)),
            call.fire(StepPassedEvent(step_result)),
            call.fire(ScenarioPassedEvent(scenario_result)),
        ]


async def test_fn_scenario_interrupt(*, runner: MonotonicScenarioRunner,
                                     dispatcher_: Mock,
                                     interrupt_exception: Type[BaseException]):
    with given:
        original_exception = interrupt_exception("interrupt")
        step_mock = Mock(side_effect=original_exception)
        vscenario = make_fn_scenario(step_mock)

    with when, raises(BaseException) as exc:
        await runner.run_scenario(vscenario)

    with then("ScenarioInterrupted is raised"):
        assert exc.type is ScenarioInterrupted
        scenario_interrupted = cast(ScenarioInterrupted, exc.value)
        # _run_fn_step catches interrupt and raises StepInterrupted,
        # but run_scenario extracts the original exc_info from StepInterrupted
        assert scenario_interrupted.exc_info.value == original_exception

    with then("scenario result is failed and has step result"):
        scenario_result = scenario_interrupted.scenario_result
        assert scenario_result.is_failed()

        assert len(scenario_result.step_results) == 1
        step_result = scenario_result.step_results[0]
        assert step_result.is_failed()
        assert step_result.exc_info.value == original_exception

    with then("ScenarioFailedEvent fired"):
        assert dispatcher_.mock_calls == [
            call.fire(ScenarioRunEvent(scenario_result)),
            call.fire(ScenarioFailedEvent(scenario_result)),
        ]
