import pytest
from baby_steps import given, then, when

from vedro.plugins.director.rich._differ import AdvancedDiffer


@pytest.fixture
def differ() -> AdvancedDiffer:
    return AdvancedDiffer()


def test_compare_equal(differ: AdvancedDiffer):
    with given:
        a = ["line1", "line2", "line3"]
        b = ["line1", "line2", "line3"]

    with when:
        result = list(differ.compare(a, b))

    with then:
        assert result == ["  line1", "  line2", "  line3"]


def test_compare_insert(differ: AdvancedDiffer):
    with given:
        a = ["line1", "line2"]
        b = ["line1", "line2", "line3"]

    with when:
        result = list(differ.compare(a, b))

    with then:
        assert result == ["  line1", "  line2", "+ line3"]


def test_compare_delete(differ: AdvancedDiffer):
    with given:
        a = ["line1", "line2", "line3"]
        b = ["line1", "line2"]

    with when:
        result = list(differ.compare(a, b))

    with then:
        assert result == ["  line1", "  line2", "- line3"]


def test_compare_replace(differ: AdvancedDiffer):
    with given:
        a = ["line1", "line2", "line3"]
        b = ["line1", "line2_changed", "line3"]

    with when:
        result = list(differ.compare(a, b))

    with then:
        assert result == ["  line1", "- line2", "+ line2_changed", "  line3"]


def test_compare_fancy_replace(differ: AdvancedDiffer):
    with given:
        a = ["line1", "line2_changed1", "line3"]
        b = ["line1", "line2_changed2", "line3"]

    with when:
        result = list(differ.compare(a, b))

    with then:
        assert result == [
            "  line1",
            "- line2_changed1",
            "?              ^\n",
            "+ line2_changed2",
            "?              ^\n",
            "  line3",
        ]
