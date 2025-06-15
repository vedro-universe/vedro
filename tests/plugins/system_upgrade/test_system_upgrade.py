from typing import Callable, Tuple
from urllib.error import URLError

import pytest
from baby_steps import given, then, when

from vedro.core import Dispatcher, Report
from vedro.core.exp.local_storage import LocalStorage
from vedro.events import CleanupEvent
from vedro.plugins.system_upgrade import SystemUpgrade, SystemUpgradePlugin

from ._utils import (
    dispatcher,
    fire_startup_event,
    gen_next_version,
    gen_prev_version,
    get_cur_version,
    mocked_error_response,
    mocked_response,
    now,
    system_upgrade,
    system_upgrade_storage,
)

__all__ = ("dispatcher", "system_upgrade", "system_upgrade_storage",)  # fixtures


@pytest.mark.usefixtures(system_upgrade.__name__)
async def test_update_available_no_last_request(*, dispatcher: Dispatcher):
    with given:
        cur_version = get_cur_version()
        new_version = gen_next_version(cur_version)

        with mocked_response(new_version=new_version, wait_for_calls=1) as patched:
            await fire_startup_event(dispatcher)

        report = Report()
        cleanup_event = CleanupEvent(report)

    with when:
        await dispatcher.fire(cleanup_event)

    with then:
        assert report.summary == [
            f"(!) Vedro update available: {cur_version} → {new_version}"
            " | https://vedro.io/changelog"
        ]
        assert patched.assert_called_once() is None


async def test_update_available_expired_last_request(
    *,
    dispatcher: Dispatcher,
    system_upgrade_storage: Tuple[SystemUpgradePlugin, LocalStorage]
):
    with given:
        _, local_storage = system_upgrade_storage
        await local_storage.put("last_request_ts", now() - SystemUpgrade.update_check_interval)

        cur_version = get_cur_version()
        new_version = gen_next_version(cur_version)
        with mocked_response(new_version=new_version, wait_for_calls=1) as patched:
            await fire_startup_event(dispatcher)

        report = Report()
        cleanup_event = CleanupEvent(report)

    with when:
        await dispatcher.fire(cleanup_event)

    with then:
        assert report.summary == [
            f"(!) Vedro update available: {cur_version} → {new_version}"
            " | https://vedro.io/changelog"
        ]
        assert patched.assert_called_once() is None


async def test_update_available_fresh_last_request(
    *,
    dispatcher: Dispatcher,
    system_upgrade_storage: Tuple[SystemUpgradePlugin, LocalStorage]
):
    with given:
        _, local_storage = system_upgrade_storage
        await local_storage.put("last_request_ts", now())

        new_version = gen_next_version(get_cur_version())
        with mocked_response(new_version=new_version) as patched:
            await fire_startup_event(dispatcher)

        report = Report()
        cleanup_event = CleanupEvent(report)

    with when:
        await dispatcher.fire(cleanup_event)

    with then:
        assert report.summary == []
        assert patched.assert_not_called() is None


@pytest.mark.usefixtures(system_upgrade.__name__)
@pytest.mark.parametrize("gen_version", [gen_prev_version, lambda _: get_cur_version()])
async def test_update_not_available(gen_version: Callable[[str], str], *, dispatcher: Dispatcher):
    with given:
        new_version = gen_version(get_cur_version())
        with mocked_response(new_version=new_version, wait_for_calls=1) as patched:
            await fire_startup_event(dispatcher)

        report = Report()
        cleanup_event = CleanupEvent(report)

    with when:
        await dispatcher.fire(cleanup_event)

    with then:
        assert report.summary == []
        assert patched.assert_called_once() is None


@pytest.mark.usefixtures(system_upgrade.__name__)
async def test_update_error(dispatcher: Dispatcher):
    with given:
        with mocked_error_response(URLError("msg"), wait_for_calls=1) as patched:
            await fire_startup_event(dispatcher)

        report = Report()
        cleanup_event = CleanupEvent(report)

    with when:
        await dispatcher.fire(cleanup_event)

    with then:
        assert report.summary == []
        assert patched.assert_called_once() is None


@pytest.mark.usefixtures(system_upgrade.__name__)
async def test_thread_stop(dispatcher: Dispatcher):
    with given:
        report = Report()
        cleanup_event = CleanupEvent(report)

    with when:
        await dispatcher.fire(cleanup_event)

    with then:
        assert report.summary == []
