from pathlib import Path

from baby_steps import given, then, when
from pytest import raises

from vedro.core.scenario_finder.scenario_file_finder import FileFilter


def test_file_filter():
    with raises(BaseException) as exc:
        FileFilter()

    assert exc.type is TypeError
    assert "Can't instantiate abstract class FileFilter" in str(exc.value)


def test_file_filter_repr():
    with given:
        # Create a concrete implementation for testing
        class ConcreteFileFilter(FileFilter):
            def filter(self, path: Path) -> bool:
                return False

        file_filter = ConcreteFileFilter()

    with when:
        representation = repr(file_filter)

    with then:
        assert representation == "<ConcreteFileFilter>"
