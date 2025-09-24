from pathlib import Path

import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro.core.scenario_finder.scenario_file_finder import ExtFilter


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
    with raises(BaseException) as exc:
        ExtFilter(only=[".py"], ignore=[".sh"])

    assert exc.type is ValueError
    assert str(exc.value) == "Use 'only' or 'ignore' (not both)"


def test_ext_filter_repr_no_params():
    with given:
        ext_filter = ExtFilter()

    with when:
        representation = repr(ext_filter)

    with then:
        assert representation == "ExtFilter()"


def test_ext_filter_repr_with_only():
    with given:
        ext_filter = ExtFilter(only=[".py", ".sh"])

    with when:
        representation = repr(ext_filter)

    with then:
        assert representation == "ExtFilter(only=['.py', '.sh'])"


def test_ext_filter_repr_with_ignore():
    with given:
        ext_filter = ExtFilter(ignore=[".pyc", ".pyo"])

    with when:
        representation = repr(ext_filter)

    with then:
        assert representation == "ExtFilter(ignore=['.pyc', '.pyo'])"
