from typing import cast

import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro._core._dispatcher import Dispatcher
from vedro._core._report import Report
from vedro._events import CleanupEvent
from vedro.plugins import Terminator


@pytest.fixture()
def dispatcher():
    return Dispatcher()


@pytest.fixture()
def plugin(dispatcher):
    plugin = Terminator()
    plugin.subscribe(dispatcher)
    return plugin


@pytest.mark.asyncio
async def test_terminator_plugin_passed(*, plugin: Terminator, dispatcher: Dispatcher):
    with given:
        report = Report()
        report.passed = 1
        report.failed = 0

    with when, raises(BaseException) as exception:
        await dispatcher.fire(CleanupEvent(report))

    with then:
        assert exception.type is SystemExit
        assert cast(SystemExit, exception.value).code == 0


@pytest.mark.asyncio
async def test_terminator_plugin_failed(*, plugin: Terminator, dispatcher: Dispatcher):
    with given:
        report = Report()
        report.passed = 0
        report.failed = 1

    with when, raises(BaseException) as exception:
        await dispatcher.fire(CleanupEvent(report))

    with then:
        assert exception.type is SystemExit
        assert cast(SystemExit, exception.value).code == 1


@pytest.mark.asyncio
async def test_terminator_plugin_no_passed(*, plugin: Terminator, dispatcher: Dispatcher):
    with given:
        report = Report()
        report.passed = 0
        report.failed = 0

    with when, raises(BaseException) as exception:
        await dispatcher.fire(CleanupEvent(report))

    with then:
        assert exception.type is SystemExit
        assert cast(SystemExit, exception.value).code == 1
