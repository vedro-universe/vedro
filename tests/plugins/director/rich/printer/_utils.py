import sys
from typing import Any
from unittest.mock import Mock

import pytest
from rich.console import Console, ConsoleDimensions

from vedro.core import ExcInfo
from vedro.plugins.director.rich import RichPrinter


@pytest.fixture()
def console_() -> Mock:
    mock = Mock(Console, size=ConsoleDimensions(80, 25))
    mock.encoding = "utf-8"
    return mock


@pytest.fixture()
def printer(console_: Mock) -> RichPrinter:
    return RichPrinter(lambda: console_,
                       traceback_factory=TestTraceback,
                       pretty_factory=TestPretty,
                       pretty_diff_factory=TestPrettyDiff)


@pytest.fixture()
def exc_info() -> ExcInfo:
    try:
        raise KeyError()
    except KeyError:
        _, value, traceback = sys.exc_info()
    return ExcInfo(type(value), value, traceback)


class _TestBase:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._args = args
        self._kwargs = kwargs

    def __eq__(self, other: Any) -> bool:
        if self.__class__ != other.__class__:
            return False
        return (self._args == other._args) and (self._kwargs == other._kwargs)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._args!r}, {self._kwargs!r})"


class TestTraceback(_TestBase):
    pass


class TestPretty(_TestBase):
    pass


class TestPrettyDiff(_TestBase):
    pass
