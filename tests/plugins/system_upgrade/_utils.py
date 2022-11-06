from contextlib import contextmanager
from typing import Any, Callable
from unittest.mock import patch

import pytest

import vedro
from vedro.core import Dispatcher
from vedro.plugins.system_upgrade import SystemUpgrade, SystemUpgradePlugin


@pytest.fixture()
def dispatcher() -> Dispatcher:
    return Dispatcher()


@pytest.fixture()
def system_upgrade(dispatcher: Dispatcher) -> SystemUpgradePlugin:
    tagger = SystemUpgradePlugin(SystemUpgrade)
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


@contextmanager
def mocked_response(new_version: str):
    return_value = urlopen(lambda: f'{{"version": "{new_version}"}}'.encode())
    with patch("urllib.request.urlopen", return_value=return_value) as patched:
        yield patched


@contextmanager
def mocked_error_response(exception: BaseException):
    def raise_():
        raise exception

    with patch("urllib.request.urlopen", return_value=urlopen(raise_)) as patched:
        yield patched


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
