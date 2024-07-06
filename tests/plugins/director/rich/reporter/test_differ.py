from typing import List

import pytest
from baby_steps import given, then, when

from vedro.plugins.director.rich._differ import AdvancedDiffer


@pytest.fixture
def differ() -> AdvancedDiffer:
    return AdvancedDiffer()


def test_compare_equal(*, differ: AdvancedDiffer):
    with given:
        a = ["line1", "line2", "line3"]
        b = ["line1", "line2", "line3"]

    with when:
        result = list(differ.compare(a, b))

    with then:
        assert result == ["  line1", "  line2", "  line3"]


def test_compare_insert(*, differ: AdvancedDiffer):
    with given:
        a = ["line1", "line2"]
        b = ["line1", "line2", "line3"]

    with when:
        result = list(differ.compare(a, b))

    with then:
        assert result == ["  line1", "  line2", "+ line3"]


def test_compare_delete(*, differ: AdvancedDiffer):
    with given:
        a = ["line1", "line2", "line3"]
        b = ["line1", "line2"]

    with when:
        result = list(differ.compare(a, b))

    with then:
        assert result == ["  line1", "  line2", "- line3"]


def test_compare_replace(*, differ: AdvancedDiffer):
    with given:
        a = ["line1", "line2", "line3"]
        b = ["line1", "line2_changed", "line3"]

    with when:
        result = list(differ.compare(a, b))

    with then:
        assert result == ["  line1", "- line2", "+ line2_changed", "  line3"]


def test_compare_fancy_replace(*, differ: AdvancedDiffer):
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


def test_compare_fancy_replace_multiple_groups(differ: AdvancedDiffer):
    with given:
        a = ["line1", "line2_changed1", "line3", "line4", "line5_changed1", "line6"]
        b = ["line1", "line2_changed2", "line3", "line4", "line5_changed2", "line6"]

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
            "  line4",
            "- line5_changed1",
            "?              ^\n",
            "+ line5_changed2",
            "?              ^\n",
            "  line6",
        ]


@pytest.mark.parametrize("context_lines", [0, 1, 2])
def test_compare_unified_equal(context_lines: int, *, differ: AdvancedDiffer):
    with given:
        a = ["line1", "line2", "line3"]
        b = ["line1", "line2", "line3"]

    with when:
        result = list(differ.compare_unified(a, b, context_lines))

    with then:
        assert result == []


@pytest.mark.parametrize(("context_lines", "expected"), [
    (0, ["+ line3"]),
    (1, ["  line2", "+ line3"]),
    (2, ["  line1", "  line2", "+ line3"])
])
def test_compare_unified_insert(context_lines: int, expected: List[str], *,
                                differ: AdvancedDiffer):
    with given:
        a = ["line1", "line2"]
        b = ["line1", "line2", "line3"]

    with when:
        result = list(differ.compare_unified(a, b, context_lines))

    with then:
        assert result == expected


@pytest.mark.parametrize(("context_lines", "expected"), [
    (0, ["- line3"]),
    (1, ["  line2", "- line3"]),
    (2, ["  line1", "  line2", "- line3"])
])
def test_compare_unified_delete(context_lines: int, expected: List[str], *,
                                differ: AdvancedDiffer):
    with given:
        a = ["line1", "line2", "line3"]
        b = ["line1", "line2"]

    with when:
        result = list(differ.compare_unified(a, b, context_lines))

    with then:
        assert result == expected


@pytest.mark.parametrize(("context_lines", "expected"), [
    (0, ["- line2", "+ line2_changed"]),
    (1, ["  line1", "- line2", "+ line2_changed", "  line3"]),
    (2, ["  line1", "- line2", "+ line2_changed", "  line3"])
])
def test_compare_unified_replace(context_lines: int, expected: List[str], *,
                                 differ: AdvancedDiffer):
    with given:
        a = ["line1", "line2", "line3"]
        b = ["line1", "line2_changed", "line3"]

    with when:
        result = list(differ.compare_unified(a, b, context_lines))

    with then:
        assert result == expected


@pytest.mark.parametrize(("context_lines", "expected"), [
    (0, [
        "- line2_changed1",
        "?              ^\n",
        "+ line2_changed2",
        "?              ^\n"
    ]),
    (1, [
        "  line1",
        "- line2_changed1",
        "?              ^\n",
        "+ line2_changed2",
        "?              ^\n",
        "  line3"
    ]),
    (2, [
        "  line1",
        "- line2_changed1",
        "?              ^\n",
        "+ line2_changed2",
        "?              ^\n",
        "  line3"
    ]),
])
def test_compare_unified_fancy_replace(context_lines: int, expected: List[str], *,
                                       differ: AdvancedDiffer):
    with given:
        a = ["line1", "line2_changed1", "line3"]
        b = ["line1", "line2_changed2", "line3"]

    with when:
        result = list(differ.compare_unified(a, b, context_lines))

    with then:
        assert result == expected


@pytest.mark.parametrize(("context_lines", "expected"), [
    (0, [
        "- line2_changed1",
        "?              ^\n",
        "+ line2_changed2",
        "?              ^\n",
        "...",
        "- line5_changed1",
        "?              ^\n",
        "+ line5_changed2",
        "?              ^\n"
    ]),
    (1, [
        "  line1",
        "- line2_changed1",
        "?              ^\n",
        "+ line2_changed2",
        "?              ^\n",
        "  line3",
        "  line4",
        "- line5_changed1",
        "?              ^\n",
        "+ line5_changed2",
        "?              ^\n",
        "  line6"
    ]),
    (2, [
        "  line1",
        "- line2_changed1",
        "?              ^\n",
        "+ line2_changed2",
        "?              ^\n",
        "  line3",
        "  line4",
        "- line5_changed1",
        "?              ^\n",
        "+ line5_changed2",
        "?              ^\n",
        "  line6"
    ]),
])
def test_compare_unified_fancy_replace_multiple_groups(context_lines: int, expected: List[str], *,
                                                       differ: AdvancedDiffer):
    with given:
        a = ["line1", "line2_changed1", "line3", "line4", "line5_changed1", "line6"]
        b = ["line1", "line2_changed2", "line3", "line4", "line5_changed2", "line6"]

    with when:
        result = list(differ.compare_unified(a, b, context_lines))

    with then:
        assert result == expected
