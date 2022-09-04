from unittest.mock import Mock, call

import pytest
from baby_steps import given, then, when

from vedro.core import Dispatcher, ScenarioStatus, StepStatus
from vedro.events import (
    ScenarioFailedEvent,
    ScenarioPassedEvent,
    ScenarioRunEvent,
    ScenarioSkippedEvent,
)
from vedro.plugins.director import (
    DirectorInitEvent,
    DirectorPlugin,
    PyCharmReporter,
    PyCharmReporterPlugin,
)

from ._utils import (
    director,
    dispatcher,
    fire_arg_parsed_event,
    make_exc_info,
    make_scenario_result,
    make_step_result,
    printer_,
    pycharm_reporter,
)

__all__ = ("dispatcher", "pycharm_reporter", "director", "printer_")  # fixtures


@pytest.mark.asyncio
async def test_subscribe(*, dispatcher: Dispatcher):
    with given:
        director_ = Mock(DirectorPlugin)

        reporter = PyCharmReporterPlugin(PyCharmReporter)
        reporter.subscribe(dispatcher)

    with when:
        await dispatcher.fire(DirectorInitEvent(director_))

    with then:
        assert director_.mock_calls == [
            call.register("pycharm", reporter)
        ]


@pytest.mark.asyncio
@pytest.mark.usefixtures(pycharm_reporter.__name__)
async def test_scenario_run(*, dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher)

        scenario_result = make_scenario_result()
        event = ScenarioRunEvent(scenario_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert printer_.mock_calls == [
            call.console.out("##teamcity[testStarted "
                             f"name='{scenario_result.scenario.subject}' "
                             f"locationHint='{scenario_result.scenario.path}']")
        ]


@pytest.mark.asyncio
@pytest.mark.usefixtures(pycharm_reporter.__name__)
async def test_scenario_passed(*, dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher)

        scenario_result = make_scenario_result().mark_passed() \
                                                .set_started_at(1.0).set_ended_at(3.0)
        event = ScenarioPassedEvent(scenario_result)

    with when:
        await dispatcher.fire(event)

    with then:
        subject = scenario_result.scenario.subject
        assert printer_.mock_calls == [
            call.print_scenario_subject(subject, ScenarioStatus.PASSED, prefix=" "),
            call.console.out(f"##teamcity[testFinished name='{subject}' duration='2000']")
        ]


@pytest.mark.asyncio
@pytest.mark.usefixtures(pycharm_reporter.__name__)
async def test_scenario_failed(*, dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher)

        scenario_result = make_scenario_result().mark_failed() \
                                                .set_started_at(1.0).set_ended_at(3.0)
        event = ScenarioFailedEvent(scenario_result)

    with when:
        await dispatcher.fire(event)

    with then:
        subject = scenario_result.scenario.subject
        assert printer_.mock_calls == [
            call.print_scenario_subject(subject, ScenarioStatus.FAILED, prefix=" "),
            call.console.out(f"##teamcity[testFailed name='{subject}' message='' details='']"),
            call.console.out(f"##teamcity[testFinished name='{subject}' duration='2000']")
        ]


@pytest.mark.asyncio
@pytest.mark.usefixtures(pycharm_reporter.__name__)
@pytest.mark.parametrize("show_internal_calls", [False, True])
async def test_scenario_failed_with_steps(show_internal_calls: bool, *,
                                          dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher, show_internal_calls=show_internal_calls)

        scenario_result = make_scenario_result().set_started_at(1.0).set_ended_at(5.0)

        step_result_passed = make_step_result().mark_passed()
        scenario_result.add_step_result(step_result_passed)

        exc_info = make_exc_info(AssertionError())
        step_result_failed = make_step_result().mark_failed().set_exc_info(exc_info)
        scenario_result.add_step_result(step_result_failed)

        event = ScenarioFailedEvent(scenario_result.mark_failed())

    with when:
        await dispatcher.fire(event)

    with then:
        subject = scenario_result.scenario.subject
        assert printer_.mock_calls == [
            call.print_scenario_subject(subject, ScenarioStatus.FAILED, prefix=" "),

            call.print_step_name(step_result_passed.step_name, StepStatus.PASSED, prefix=" " * 3),
            call.print_step_name(step_result_failed.step_name, StepStatus.FAILED, prefix=" " * 3),
            call.print_exception(exc_info, show_internal_calls=show_internal_calls),

            call.console.out(f"##teamcity[testFailed name='{subject}' message='' details='']"),
            call.console.out(f"##teamcity[testFinished name='{subject}' duration='4000']")
        ]


@pytest.mark.asyncio
@pytest.mark.usefixtures(pycharm_reporter.__name__)
async def test_scenario_failed_with_scope(*, dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher)

        scenario_result = make_scenario_result().set_started_at(1.0).set_ended_at(3.0)

        exc_info = make_exc_info(AssertionError())
        step_result = make_step_result().mark_failed().set_exc_info(exc_info)
        scenario_result.add_step_result(step_result)

        scope = {"key": "val"}
        scenario_result.set_scope(scope)

        event = ScenarioFailedEvent(scenario_result.mark_failed())

    with when:
        await dispatcher.fire(event)

    with then:
        subject = scenario_result.scenario.subject
        assert printer_.mock_calls == [
            call.print_scenario_subject(subject, ScenarioStatus.FAILED, prefix=" "),

            call.print_step_name(step_result.step_name, StepStatus.FAILED, prefix=" " * 3),
            call.print_exception(exc_info, show_internal_calls=False),
            call.print_scope(scope),

            call.console.out(f"##teamcity[testFailed name='{subject}' message='' details='']"),
            call.console.out(f"##teamcity[testFinished name='{subject}' duration='2000']")
        ]


@pytest.mark.asyncio
@pytest.mark.usefixtures(pycharm_reporter.__name__)
async def test_scenario_skipped(*, dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher)

        scenario_result = make_scenario_result().mark_skipped() \
                                                .set_started_at(1.0).set_ended_at(3.0)
        event = ScenarioSkippedEvent(scenario_result)

    with when:
        await dispatcher.fire(event)

    with then:
        subject = scenario_result.scenario.subject
        assert printer_.mock_calls == [
            call.print_scenario_subject(subject, ScenarioStatus.SKIPPED, prefix=" "),
            call.console.out(f"##teamcity[testIgnored name='{subject}']")
        ]


@pytest.mark.asyncio
@pytest.mark.usefixtures(pycharm_reporter.__name__)
async def test_scenario_skipped_disabled(*, dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher, show_skipped=False)

        scenario_result = make_scenario_result().mark_skipped()
        event = ScenarioSkippedEvent(scenario_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert printer_.mock_calls == []
