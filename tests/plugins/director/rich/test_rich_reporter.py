from baby_steps import then, when

from vedro.plugins.director import Reporter, RichReporterPlugin


def test_rich_reporter():
    with when:
        reporter = RichReporterPlugin()

    with then:
        assert isinstance(reporter, Reporter)
