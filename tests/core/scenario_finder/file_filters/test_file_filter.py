from pytest import raises

from vedro.core.scenario_finder.scenario_file_finder import FileFilter


def test_file_filter():
    with raises(BaseException) as exc_info:
        FileFilter()

    assert exc_info.type is TypeError
    assert "Can't instantiate abstract class FileFilter" in str(exc_info.value)
