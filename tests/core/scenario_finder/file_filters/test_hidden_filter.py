from pathlib import Path

import pytest

from vedro._core._scenario_finder._file_filters import HiddenFilter


@pytest.mark.parametrize(("value", "expected"), [
    (".DS_Store", True),
    ("/tmp/.DS_Store", True),
    #
    ("main.py", False),
    ("/tmp/main.py", False),
])
def test_hidden_file_filter(value: str, expected: bool):
    hidden_filter = HiddenFilter()

    filtered = hidden_filter.filter(Path(value))
    assert filtered is expected
