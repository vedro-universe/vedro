from vedro import given, scenario, then, when
from vedro.core import Report

from ._helpers import format_ts, make_json_formatter


@scenario
def format_cleanup_event():
    with given:
        formatter = make_json_formatter()
        report = Report()

    with when:
        event = formatter.format_cleanup_event(report)

    with then:
        assert event == {
            "event": "cleanup",
            "timestamp": format_ts(formatter.time_fn()),
            "report": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "elapsed": 0,
                "interrupted": None,
            }
        }
