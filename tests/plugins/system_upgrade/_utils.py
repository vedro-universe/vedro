from contextlib import contextmanager
from pathlib import Path
from time import sleep, time
from typing import Any, Callable, Tuple, cast
from unittest.mock import MagicMock, patch

import pytest

import vedro
from vedro.core import Config, Dispatcher
from vedro.core import MonotonicScenarioScheduler as Scheduler
from vedro.core.exp.local_storage import LocalStorage, create_local_storage
from vedro.events import ConfigLoadedEvent, StartupEvent
from vedro.plugins.system_upgrade import SystemUpgrade, SystemUpgradePlugin


@pytest.fixture()
def dispatcher() -> Dispatcher:
    return Dispatcher()


async def make_system_upgrade(dispatcher: Dispatcher,
                              tmp_path: Path
                              ) -> Tuple[SystemUpgradePlugin, Callable[[], LocalStorage]]:
    local_storage = None

    def _create_local_storage(*args, **kwargs) -> LocalStorage:
        nonlocal local_storage
        local_storage = create_local_storage(*args, **kwargs)
        return local_storage

    def _get_local_storage() -> LocalStorage:
        nonlocal local_storage
        return cast(LocalStorage, local_storage)

    plugin = SystemUpgradePlugin(SystemUpgrade, local_storage_factory=_create_local_storage)
    plugin.subscribe(dispatcher)

    await fire_config_loaded_event(dispatcher, tmp_path)

    return plugin, _get_local_storage


@pytest.fixture()
async def system_upgrade(dispatcher: Dispatcher, tmp_path: Path) -> SystemUpgradePlugin:
    plugin, *_ = await make_system_upgrade(dispatcher, tmp_path)
    return plugin


class urlopen:
    def __init__(self, callable_: Callable[[], bytes]) -> None:
        self._callable = callable_

    def __enter__(self) -> "urlopen":
        return self

    def __exit__(self, *args: Any, **kwargs: Any) -> None:
        pass

    def read(self) -> bytes:
        return self._callable()


def _wait_for_mock_calls(patched: MagicMock, *,
                         expected: int, attempts: int = 3, delay: float = 0.01) -> None:
    attempt = 1
    while attempt <= attempts:
        if patched.call_count >= expected:
            break
        sleep(delay)
        attempt += 1


@contextmanager
def mocked_response(new_version: str, *, wait_for_calls: int = 0):
    return_value = urlopen(lambda: f'{{"version": "{new_version}"}}'.encode())
    with patch("urllib.request.urlopen", return_value=return_value) as patched:
        yield patched
        _wait_for_mock_calls(patched,  expected=wait_for_calls)


@contextmanager
def mocked_error_response(exception: BaseException, *, wait_for_calls: int = 0):
    def raise_():
        raise exception

    with patch("urllib.request.urlopen", return_value=urlopen(raise_)) as patched:
        yield patched
        _wait_for_mock_calls(patched, expected=wait_for_calls)


def get_cur_version() -> str:
    return vedro.__version__


def gen_next_version(version: str) -> str:
    major, minor, patch = tuple(int(x) for x in version.split("."))
    return ".".join(map(str, (major + 1, minor, patch)))


def gen_prev_version(version: str) -> str:
    major, minor, patch = tuple(int(x) for x in version.split("."))
    return ".".join(map(str, (major - 1, minor, patch)))


async def fire_config_loaded_event(dispatcher: Dispatcher, tmp_path: Path) -> None:
    class _Config(Config):
        project_dir = tmp_path

    config_loaded_event = ConfigLoadedEvent(_Config.project_dir, _Config)
    await dispatcher.fire(config_loaded_event)


async def fire_startup_event(dispatcher: Dispatcher) -> None:
    scheduler = Scheduler([])
    startup_event = StartupEvent(scheduler)
    await dispatcher.fire(startup_event)


def now() -> int:
    return int(time())
