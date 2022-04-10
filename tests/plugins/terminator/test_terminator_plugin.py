from typing import cast
from unittest.mock import Mock

import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro.core import Dispatcher, Report, ScenarioResult, VirtualScenario
from vedro.events import CleanupEvent
from vedro.plugins.terminator import Terminator, TerminatorPlugin


@pytest.fixture()
def dispatcher() -> Dispatcher:
    return Dispatcher()


@pytest.fixture()
def terminator(dispatcher: Dispatcher):
    terminator = TerminatorPlugin(Terminator)
    terminator.subscribe(dispatcher)
    return terminator


def make_scenario_result() -> ScenarioResult:
    scenario_ = Mock(VirtualScenario)
    return ScenarioResult(scenario_)


@pytest.mark.asyncio
async def test_terminator_plugin_passed(*, terminator: TerminatorPlugin, dispatcher: Dispatcher):
    with given:
        report = Report()
        scenario_result = make_scenario_result().mark_passed()
        report.add_result(scenario_result)

    with when, raises(BaseException) as exception:
        await dispatcher.fire(CleanupEvent(report))

    with then:
        assert exception.type is SystemExit
        assert cast(SystemExit, exception.value).code == 0


@pytest.mark.asyncio
async def test_terminator_plugin_failed(*, terminator: TerminatorPlugin, dispatcher: Dispatcher):
    with given:
        report = Report()
        scenario_result = make_scenario_result().mark_failed()
        report.add_result(scenario_result)

    with when, raises(BaseException) as exception:
        await dispatcher.fire(CleanupEvent(report))

    with then:
        assert exception.type is SystemExit
        assert cast(SystemExit, exception.value).code == 1


@pytest.mark.asyncio
async def test_terminator_plugin_no_passed(*, terminator: TerminatorPlugin,
                                           dispatcher: Dispatcher):
    with given:
        report = Report()

    with when, raises(BaseException) as exception:
        await dispatcher.fire(CleanupEvent(report))

    with then:
        assert exception.type is SystemExit
        assert cast(SystemExit, exception.value).code == 1
