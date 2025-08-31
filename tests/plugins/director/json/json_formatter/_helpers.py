from time import monotonic
from typing import Optional
from unittest.mock import Mock

from vedro.core.exc_info import TracebackFilter
from vedro.plugins.director.json import JsonFormatter
from vedro.plugins.director.json._json_formatter import TimeFunction

__all__ = ("make_tb_filter", "make_time_fn", "make_json_formatter",
           "format_ts",)


def make_tb_filter() -> TracebackFilter:
    return Mock(spec_set=TracebackFilter)


def make_time_fn() -> TimeFunction:
    return Mock(spec_set=TimeFunction, return_value=monotonic())


def make_json_formatter(tb_filter: Optional[TracebackFilter] = None,
                        time_fn: Optional[TimeFunction] = None) -> JsonFormatter:
    if tb_filter is None:
        tb_filter = make_tb_filter()
    if time_fn is None:
        time_fn = make_time_fn()
    return JsonFormatter(tb_filter, time_fn=time_fn)


def format_ts(time: float) -> int:
    return int(time * 1000)
