from typing import Type, cast

import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro.core import Dispatcher, Report
from vedro.events import CleanupEvent
from vedro.plugins.terminator import TerminatorPlugin

from ._utils import (
    dispatcher,
    make_aggregated_result,
    make_exc_info,
    make_scenario_result,
    terminator,
)

__all__ = ("dispatcher", "terminator")  # fixtures


@pytest.mark.asyncio
async def test_passed(*, terminator: TerminatorPlugin, dispatcher: Dispatcher):
    with given:
        report = Report()
        scenario_result = make_scenario_result().mark_passed()
        report.add_result(make_aggregated_result(scenario_result))

    with when, raises(BaseException) as exception:
        await dispatcher.fire(CleanupEvent(report))

    with then:
        assert exception.type is SystemExit
        assert cast(SystemExit, exception.value).code == 0


@pytest.mark.asyncio
async def test_failed(*, terminator: TerminatorPlugin, dispatcher: Dispatcher):
    with given:
        report = Report()
        scenario_result = make_scenario_result().mark_failed()
        report.add_result(make_aggregated_result(scenario_result))

    with when, raises(BaseException) as exception:
        await dispatcher.fire(CleanupEvent(report))

    with then:
        assert exception.type is SystemExit
        assert cast(SystemExit, exception.value).code == 1


@pytest.mark.asyncio
async def test_no_passed(*, terminator: TerminatorPlugin, dispatcher: Dispatcher):
    with given:
        report = Report()

    with when, raises(BaseException) as exception:
        await dispatcher.fire(CleanupEvent(report))

    with then:
        assert exception.type is SystemExit
        assert cast(SystemExit, exception.value).code == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("exception", [KeyboardInterrupt, SystemExit])
async def test_interrupted(exception: Type[BaseException], *,
                           terminator: TerminatorPlugin, dispatcher: Dispatcher):
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


@pytest.mark.asyncio
async def test_interrupted_sysexit_with_code(*, terminator: TerminatorPlugin,
                                             dispatcher: Dispatcher):
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
