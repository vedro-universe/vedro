from baby_steps import then, when

from vedro.plugins.director import Reporter, RichReporter


def test_rich_reporter():
    with when:
        reporter = RichReporter()

    with then:
        assert isinstance(reporter, Reporter)
