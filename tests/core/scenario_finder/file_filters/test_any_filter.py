from pathlib import Path
from typing import List
from unittest.mock import Mock

import pytest

from vedro._core._scenario_finder._file_filters import AnyFilter, FileFilter


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
