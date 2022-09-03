import sys
from typing import Any
from unittest.mock import Mock

import pytest
from rich.console import Console

from vedro.core import ExcInfo
from vedro.plugins.director.rich import RichPrinter


class TestTraceback:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._args = args
        self._kwargs = kwargs

    def __eq__(self, other: Any) -> bool:
        if self.__class__ != other.__class__:
            return False
        return (self._args == other._args) and (self._kwargs == other._kwargs)


@pytest.fixture()
def console_() -> Mock:
    return Mock(Console)


@pytest.fixture()
def printer(console_: Mock) -> RichPrinter:
    return RichPrinter(lambda: console_,
                       traceback_factory=lambda *args, **kwargs: TestTraceback(*args, **kwargs))


@pytest.fixture()
def exc_info() -> ExcInfo:
    try:
        raise KeyError()
    except KeyError:
        _, value, traceback = sys.exc_info()
    return ExcInfo(type(value), value, traceback)
