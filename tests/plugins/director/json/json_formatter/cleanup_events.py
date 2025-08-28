from traceback import extract_tb

from vedro import given, scenario, then, when
from vedro.core import Report
from vedro.core.exc_info import TracebackFilter

from ._helpers import format_ts, make_json_formatter
from ._tb_helpers import execute_and_capture_exception, generate_call_chain_modules


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


@scenario
def format_cleanup_event_with_rich_output():
    with given:
        formatter = make_json_formatter()
        report = Report()
        rich_output = "cleanup summary output"

    with when:
        event = formatter.format_cleanup_event(report, rich_output=rich_output)

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
            },
            "rich_output": rich_output
        }


@scenario
def format_cleanup_event_with_interrupted():
    with given:
        formatter = make_json_formatter(TracebackFilter(modules=[]))

        tmp_dir = generate_call_chain_modules([("main.py", "main")])
        exc_info = execute_and_capture_exception(tmp_dir / "main.py", "main")

        report = Report()
        report.set_interrupted(exc_info)

    with when:
        event = formatter.format_cleanup_event(report)

    with then:
        last_frame = extract_tb(exc_info.traceback)[-1]
        assert event == {
            "event": "cleanup",
            "timestamp": format_ts(formatter.time_fn()),
            "report": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "elapsed": 0,
                "interrupted": {
                    "type": "ZeroDivisionError",
                    "message": "division by zero",
                    "file": last_frame.filename,
                    "lineno": last_frame.lineno,
                },
            },
        }
