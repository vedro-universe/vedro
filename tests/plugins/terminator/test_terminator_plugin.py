from typing import Type, cast

import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro.core import Dispatcher, Report
from vedro.events import CleanupEvent

from ._utils import (
    dispatcher,
    fire_arg_parsed_event,
    make_aggregated_result,
    make_exc_info,
    make_scenario_result,
    terminator,
)

__all__ = ("dispatcher", "terminator")  # fixtures


@pytest.mark.usefixtures(terminator.__name__)
async def test_passed(*, dispatcher: Dispatcher):
    with given:
        report = Report()
        scenario_result = make_scenario_result().mark_passed()
        report.add_result(make_aggregated_result(scenario_result))

    with when, raises(BaseException) as exception:
        await dispatcher.fire(CleanupEvent(report))

    with then:
        assert exception.type is SystemExit
        assert cast(SystemExit, exception.value).code == 0


@pytest.mark.usefixtures(terminator.__name__)
async def test_failed(*, dispatcher: Dispatcher):
    with given:
        report = Report()
        scenario_result = make_scenario_result().mark_failed()
        report.add_result(make_aggregated_result(scenario_result))

    with when, raises(BaseException) as exception:
        await dispatcher.fire(CleanupEvent(report))

    with then:
        assert exception.type is SystemExit
        assert cast(SystemExit, exception.value).code == 1


@pytest.mark.usefixtures(terminator.__name__)
async def test_no_passed(*, dispatcher: Dispatcher):
    with given:
        report = Report()

    with when, raises(BaseException) as exception:
        await dispatcher.fire(CleanupEvent(report))

    with then:
        assert exception.type is SystemExit
        assert cast(SystemExit, exception.value).code == 1


@pytest.mark.usefixtures(terminator.__name__)
@pytest.mark.parametrize(("no_scenarios_ok", "exit_code"), [
    (False, 1),
    (True, 0),
])
async def test_no_passed_no_scenarios_ok(no_scenarios_ok: bool, exit_code: int, *,
                                         dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, no_scenarios_ok=no_scenarios_ok)

        report = Report()

    with when, raises(BaseException) as exception:
        await dispatcher.fire(CleanupEvent(report))

    with then:
        assert exception.type is SystemExit
        assert cast(SystemExit, exception.value).code == exit_code


@pytest.mark.usefixtures(terminator.__name__)
@pytest.mark.parametrize("exception", [KeyboardInterrupt, SystemExit])
async def test_interrupted(exception: Type[BaseException], *, dispatcher: Dispatcher):
    with given:
        report = Report()
        scenario_result = make_scenario_result().mark_passed()
        report.add_result(make_aggregated_result(scenario_result))

        exc_info = make_exc_info(exception())
        report.set_interrupted(exc_info)

    with when, raises(BaseException) as exception:
        await dispatcher.fire(CleanupEvent(report))

    with then:
        assert exception.type is SystemExit
        assert cast(SystemExit, exception.value).code == 130


@pytest.mark.usefixtures(terminator.__name__)
async def test_interrupted_sysexit_with_code(*, dispatcher: Dispatcher):
    with given:
        report = Report()
        scenario_result = make_scenario_result().mark_passed()
        report.add_result(make_aggregated_result(scenario_result))

        exit_code = 2
        exc_info = make_exc_info(SystemExit(exit_code))
        report.set_interrupted(exc_info)

    with when, raises(BaseException) as exception:
        await dispatcher.fire(CleanupEvent(report))

    with then:
        assert exception.type is SystemExit
        assert cast(SystemExit, exception.value).code == exit_code
