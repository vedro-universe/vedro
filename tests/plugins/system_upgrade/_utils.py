from contextlib import contextmanager
from time import sleep
from typing import Any, Callable
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from niltype import Nil

import vedro
from vedro.core import Dispatcher
from vedro.core.local_storage import LocalStorage
from vedro.plugins.system_upgrade import SystemUpgrade, SystemUpgradePlugin


@pytest.fixture()
def dispatcher() -> Dispatcher:
    return Dispatcher()


@pytest.fixture()
def system_upgrade(dispatcher: Dispatcher) -> SystemUpgradePlugin:
    local_storage_ = Mock(LocalStorage, get=AsyncMock(return_value=Nil))
    tagger = SystemUpgradePlugin(SystemUpgrade, local_storage=local_storage_)
    tagger.subscribe(dispatcher)
    return tagger


class urlopen:
    def __init__(self, callable: Callable[[], bytes]) -> None:
        self._callable = callable

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


@pytest.fixture()
def cur_version() -> str:
    return get_cur_version()


def get_cur_version() -> str:
    return vedro.__version__


def gen_next_version(version: str) -> str:
    major, minor, patch = tuple(int(x) for x in version.split("."))
    return ".".join(map(str, (major + 1, minor, patch)))


def gen_prev_version(version: str) -> str:
    major, minor, patch = tuple(int(x) for x in version.split("."))
    return ".".join(map(str, (major - 1, minor, patch)))
