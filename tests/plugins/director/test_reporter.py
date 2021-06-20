import pytest
from baby_steps import given, then, when

from vedro.plugins.director import Reporter


@pytest.mark.parametrize(("cls_name", "reporter_name"), [
    ("WordReporter", "word"),
    ("TwoWordsReporter", "two_words"),
    ("ReportGenerator", "report_generator"),
])
def test_reporter_name(cls_name: str, reporter_name: str):
    with given:
        cls = type(cls_name, (Reporter,), {})

    with when:
        reporter = cls()

    with then:
        assert reporter.name == reporter_name
