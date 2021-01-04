from pathlib import Path

import pytest
from pytest import raises

from vedro._core._scenario_finder._file_filters import ExtFilter


@pytest.mark.parametrize(("value", "expected"), [
    ("/tmp", False),
    ("/tmp/main.py", False),
    ("init.sh", False),
])
def test_ext_file_filter(value: str, expected: bool):
    ext_filter = ExtFilter()

    filtered = ext_filter.filter(Path(value))
    assert filtered is expected


@pytest.mark.parametrize(("value", "expected"), [
    ("main.py", False),
    ("init.sh", False),
    ("/tmp/main.py", False),
    #
    ("main.pyc", True),
    ("/tmp/main.pyc", True),
    ("/tmp", True),
])
def test_ext_file_filter_only(value: str, expected: bool):
    ext_filter = ExtFilter(only=[".py", ".sh"])

    filtered = ext_filter.filter(Path(value))
    assert filtered is expected


@pytest.mark.parametrize(("value", "expected"), [
    ("main.py", True),
    ("init.sh", True),
    ("/tmp/main.py", True),
    #
    ("main.pyc", False),
    ("/tmp/main.pyc", False),
    ("/tmp", False),
])
def test_ext_file_filter_ignore(value: str, expected: bool):
    ext_filter = ExtFilter(ignore=[".py", ".sh"])

    filtered = ext_filter.filter(Path(value))
    assert filtered is expected


def test_ext_file_filter_only_and_ignore():
    with raises(Exception) as exc_info:
        ExtFilter(only=[".py"], ignore=[".sh"])

    assert exc_info.type is ValueError
    assert str(exc_info.value) == "Use 'only' or 'ignore' (not both)"
