from pathlib import Path

import pytest

from vedro._core._scenario_finder._file_filters import DunderFilter


@pytest.mark.parametrize(("value", "expected"), [
    ("__pycache__", True),
    ("/tmp/__pycache__", True),
    ("__init__.py", True),
    ("/tmp/__init__.py", True),
    ("/tmp/__cache__.tar.gz", True),
    #
    ("/tmp", False),
    ("/tmp/main.py", False),
    ("/tmp/__pycache", False),
    ("main.py", False),
    ("__init.py", False),
])
def test_dunder_file_filter(value: str, expected: bool):
    dunder_filter = DunderFilter()

    filtered = dunder_filter.filter(Path(value))
    assert filtered is expected
