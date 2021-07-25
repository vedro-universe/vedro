from unittest.mock import Mock, call

import pytest
from baby_steps import given, then, when
from rich.console import Style

from vedro._core import Dispatcher, ScenarioResult, StepResult
from vedro.events import ArgParsedEvent, ScenarioFailedEvent
from vedro.plugins.director import RichReporter
from vedro.plugins.director.rich.test_utils import (
    console_,
    dispatcher,
    make_exc_info,
    make_parsed_args,
    make_scenario_result,
    make_step_result,
    make_vscenario,
    make_vstep,
    reporter,
)

__all__ = ("dispatcher", "reporter", "console_",)


@pytest.mark.asyncio
async def test_rich_reporter_scenario_failed_event_default_verbose(*, dispatcher: Dispatcher,
                                                                   reporter: RichReporter,
                                                                   console_: Mock):
    with given:
        reporter.subscribe(dispatcher)

        subject = "<subject>"
        vscenario = make_vscenario(subject=subject)
        scenario_result = ScenarioResult(vscenario).mark_failed()
        event = ScenarioFailedEvent(scenario_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert console_.mock_calls == [
            call.out(f" ✗ {subject}", style=Style.parse("red"))
        ]


@pytest.mark.asyncio
async def test_rich_reporter_scenario_failed_event_verbose0(*, dispatcher: Dispatcher,
                                                            reporter: RichReporter,
                                                            console_: Mock):
    with given:
        reporter.subscribe(dispatcher)
        event = ArgParsedEvent(make_parsed_args(verbose=0))
        await dispatcher.fire(event)

        scenario_result = make_scenario_result().mark_failed()
        event = ScenarioFailedEvent(scenario_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert console_.mock_calls == [
            call.out(f" ✗ {scenario_result.scenario_subject}", style=Style.parse("red"))
        ]


@pytest.mark.asyncio
async def test_rich_reporter_scenario_failed_event_verbose1(*, dispatcher: Dispatcher,
                                                            reporter: RichReporter,
                                                            console_: Mock):
    with given:
        reporter.subscribe(dispatcher)
        event = ArgParsedEvent(make_parsed_args(verbose=1))
        await dispatcher.fire(event)

        subject = "<subject>"
        vscenario = make_vscenario(subject=subject)

        step_name_passed = "<passed step>"
        step_result_passed = StepResult(make_vstep(name=step_name_passed)).mark_passed()
        step_name_failed = "<failed step>"
        step_result_failed = StepResult(make_vstep(name=step_name_failed)).mark_failed()
        step_result = make_step_result()

        scenario_result = make_scenario_result(vscenario, [
            step_result_passed,
            step_result_failed,
            step_result,
        ]).mark_failed()
        event = ScenarioFailedEvent(scenario_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert console_.mock_calls == [
            call.out(f" ✗ {subject}", style=Style.parse("red")),
            call.out(f"    ✔ {step_name_passed}", style=Style.parse("green")),
            call.out(f"    ✗ {step_name_failed}", style=Style.parse("red")),
        ]


@pytest.mark.asyncio
async def test_rich_reporter_scenario_failed_event_verbose2(*, dispatcher: Dispatcher,
                                                            reporter: RichReporter,
                                                            console_: Mock):
    with given:
        reporter.subscribe(dispatcher)
        event = ArgParsedEvent(make_parsed_args(verbose=2))
        await dispatcher.fire(event)

        step_result_passed = make_step_result().mark_passed()
        exc_info = make_exc_info(AssertionError())
        step_result_failed = make_step_result().mark_failed().set_exc_info(exc_info)
        step_result = make_step_result()

        scenario_result = make_scenario_result(step_results=[
            step_result_passed,
            step_result_failed,
            step_result,
        ]).mark_failed()
        event = ScenarioFailedEvent(scenario_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert console_.mock_calls[:3] == [
            call.out(f" ✗ {scenario_result.scenario_subject}", style=Style.parse("red")),
            call.out(f"    ✔ {step_result_passed.step_name}", style=Style.parse("green")),
            call.out(f"    ✗ {step_result_failed.step_name}", style=Style.parse("red")),
        ]
        name, args, kwargs = console_.mock_calls[3]
        assert "Traceback" in args[0]
        assert kwargs["style"] == Style.parse("yellow")


@pytest.mark.asyncio
async def test_rich_reporter_scenario_failed_event_verbose3(*, dispatcher: Dispatcher,
                                                            reporter: RichReporter,
                                                            console_: Mock):
    with given:
        reporter.subscribe(dispatcher)
        event = ArgParsedEvent(make_parsed_args(verbose=3))
        await dispatcher.fire(event)

        step_result_passed = make_step_result().mark_passed()
        exc_info = make_exc_info(AssertionError())
        step_result_failed = make_step_result().mark_failed().set_exc_info(exc_info)
        step_result = make_step_result()

        scenario_result = make_scenario_result(step_results=[
            step_result_passed,
            step_result_failed,
            step_result,
        ]).mark_failed()
        scenario_result.set_scope({"key_int": 1, "key_str": "val"})
        event = ScenarioFailedEvent(scenario_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert console_.mock_calls[:3] == [
            call.out(f" ✗ {scenario_result.scenario_subject}", style=Style.parse("red")),
            call.out(f"    ✔ {step_result_passed.step_name}", style=Style.parse("green")),
            call.out(f"    ✗ {step_result_failed.step_name}", style=Style.parse("red")),
        ]

        name, args, kwargs = console_.mock_calls[3]
        assert "Traceback" in args[0]
        assert kwargs["style"] == Style.parse("yellow")

        name, args, kwargs = console_.mock_calls[4]
        assert "Scope" in args[0]
        assert kwargs["style"] == Style(color="blue", bold=True)


@pytest.mark.asyncio
async def test_rich_reporter_scenario_failed_event_without_steps_verbose3(*,
                                                                          dispatcher: Dispatcher,
                                                                          reporter: RichReporter,
                                                                          console_: Mock):
    with given:
        reporter.subscribe(dispatcher)
        event = ArgParsedEvent(make_parsed_args(verbose=3))
        await dispatcher.fire(event)

        scenario_result = make_scenario_result().mark_failed()
        event = ScenarioFailedEvent(scenario_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert console_.mock_calls == [
            call.out(f" ✗ {scenario_result.scenario_subject}", style=Style.parse("red")),
        ]
