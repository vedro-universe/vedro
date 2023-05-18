from typing import Callable
from urllib.error import URLError

import pytest
from baby_steps import given, then, when

from vedro.core import Dispatcher
from vedro.core import MonotonicScenarioScheduler as Scheduler
from vedro.core import Report
from vedro.events import CleanupEvent, StartupEvent

from ._utils import (
    cur_version,
    dispatcher,
    gen_next_version,
    gen_prev_version,
    get_cur_version,
    mocked_error_response,
    mocked_response,
    system_upgrade,
)

__all__ = ("dispatcher", "system_upgrade", "cur_version")  # fixtures


@pytest.mark.asyncio
@pytest.mark.usefixtures(system_upgrade.__name__)
async def test_update_available(*, cur_version: str, dispatcher: Dispatcher):
    new_version = gen_next_version(cur_version)
    with given, mocked_response(new_version=new_version, wait_for_calls=1) as patched:
        scheduler = Scheduler([])
        startup_event = StartupEvent(scheduler)
        await dispatcher.fire(startup_event)

        report = Report()
        cleanup_event = CleanupEvent(report)

    with when:
        await dispatcher.fire(cleanup_event)

    with then:
        assert report.summary == [
            f"(!) Vedro update available: {cur_version} → {new_version}"
        ]
        assert patched.assert_called_once() is None


@pytest.mark.asyncio
@pytest.mark.usefixtures(system_upgrade.__name__)
@pytest.mark.parametrize("gen_version", [gen_prev_version, lambda _: get_cur_version()])
async def test_update_not_available(gen_version: Callable[[str], str], *,
                                    cur_version: str, dispatcher: Dispatcher):
    new_version = gen_version(cur_version)
    with given, mocked_response(new_version=new_version, wait_for_calls=1) as patched:
        scheduler = Scheduler([])
        startup_event = StartupEvent(scheduler)
        await dispatcher.fire(startup_event)

        report = Report()
        cleanup_event = CleanupEvent(report)

    with when:
        await dispatcher.fire(cleanup_event)

    with then:
        assert report.summary == []
        assert patched.assert_called_once() is None


@pytest.mark.asyncio
@pytest.mark.usefixtures(system_upgrade.__name__)
async def test_update_error(cur_version: str, dispatcher: Dispatcher):
    with given, mocked_error_response(URLError("msg"), wait_for_calls=1) as patched:
        scheduler = Scheduler([])
        startup_event = StartupEvent(scheduler)
        await dispatcher.fire(startup_event)

        report = Report()
        cleanup_event = CleanupEvent(report)

    with when:
        await dispatcher.fire(cleanup_event)

    with then:
        assert report.summary == []
        assert patched.assert_called_once() is None


@pytest.mark.asyncio
@pytest.mark.usefixtures(system_upgrade.__name__)
async def test_thread_stop(cur_version: str, dispatcher: Dispatcher):
    with given:
        report = Report()
        cleanup_event = CleanupEvent(report)

    with when:
        await dispatcher.fire(cleanup_event)

    with then:
        assert report.summary == []
