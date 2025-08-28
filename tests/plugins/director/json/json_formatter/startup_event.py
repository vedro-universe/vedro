from vedro import given, scenario, then, when

from ._helpers import format_ts, make_json_formatter


@scenario
def format_startup_event():
    with given:
        formatter = make_json_formatter()
        discovered, scheduled, skipped = 10, 8, 2

    with when:
        event = formatter.format_startup_event(discovered=discovered,
                                               scheduled=scheduled,
                                               skipped=skipped)

    with then:
        assert event == {
            "event": "startup",
            "timestamp": format_ts(formatter.time_fn()),
            "scenarios": {
                "discovered": 10,
                "scheduled": 8,
                "skipped": 2,
            }
        }


@scenario
def format_startup_event_with_rich_output():
    with given:
        formatter = make_json_formatter()
        discovered, scheduled, skipped = 5, 5, 0
        rich_output = "rich"

    with when:
        event = formatter.format_startup_event(discovered=discovered,
                                               scheduled=scheduled,
                                               skipped=skipped,
                                               rich_output=rich_output)

    with then:
        assert event == {
            "event": "startup",
            "timestamp": format_ts(formatter.time_fn()),
            "scenarios": {
                "discovered": 5,
                "scheduled": 5,
                "skipped": 0,
            },
            "rich_output": "rich"
        }
