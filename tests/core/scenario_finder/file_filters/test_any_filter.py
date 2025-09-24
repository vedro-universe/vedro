from pathlib import Path
from typing import List
from unittest.mock import Mock

import pytest
from baby_steps import given, then, when

from vedro.core.scenario_finder.scenario_file_finder import (
    AnyFilter,
    DunderFilter,
    FileFilter,
    HiddenFilter,
)


def true_filter():
    return Mock(FileFilter, filter=Mock(return_value=True))


def false_filter():
    return Mock(FileFilter, filter=Mock(return_value=False))


@pytest.mark.parametrize(("filters", "expected"), [
    ([], False),
    ([true_filter()], True),
    ([false_filter()], False),
    ([true_filter(), true_filter()], True),
    ([true_filter(), false_filter()], True),
    ([false_filter(), true_filter()], True),
    ([false_filter(), false_filter()], False),
])
def test_and_file_filter(filters: List[FileFilter], expected: bool):
    file_filter = AnyFilter(filters)
    filtered = file_filter.filter(Path("/tmp"))
    assert filtered is expected


def test_any_filter_repr_empty():
    with given:
        any_filter = AnyFilter([])

    with when:
        representation = repr(any_filter)

    with then:
        assert representation == "AnyFilter([])"


def test_any_filter_repr_with_filters():
    with given:
        filter1 = HiddenFilter()
        filter2 = DunderFilter()
        any_filter = AnyFilter([filter1, filter2])

    with when:
        representation = repr(any_filter)

    with then:
        assert representation == "AnyFilter([HiddenFilter(), DunderFilter()])"
