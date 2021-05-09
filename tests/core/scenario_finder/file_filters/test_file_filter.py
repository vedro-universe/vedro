from pytest import raises

from vedro._core._scenario_finder._file_filters import FileFilter


def test_file_filter():
    with raises(Exception) as exc_info:
        FileFilter()

    assert exc_info.type is TypeError
    assert "Can't instantiate abstract class FileFilter" in str(exc_info.value)
