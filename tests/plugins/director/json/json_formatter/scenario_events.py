from vedro import given, scenario, then, when
from vedro._test_utils import (
    make_failed_scenario_result,
    make_passed_scenario_result,
    make_scenario_result,
    make_vscenario,
)
from vedro.core import ScenarioStatus

from ._helpers import format_ts, make_json_formatter


@scenario
def format_run_scenario_event():
    with given:
        formatter = make_json_formatter()
        scenario_result = make_scenario_result(vscenario := make_vscenario())

    with when:
        event = formatter.format_scenario_run_event(scenario_result)

    with then:
        assert event == {
            "event": "scenario_run",
            "timestamp": format_ts(formatter.time_fn()),
            "scenario": {
                "id": vscenario.unique_id,
                "subject": vscenario.subject,
                "path": str(vscenario.path),
                "lineno": vscenario.lineno,
                "status": ScenarioStatus.PENDING.value,
                "elapsed": 0,
                "skip_reason": None,
            }
        }


@scenario
def format_scenario_passed_event():
    with given:
        formatter = make_json_formatter()
        scenario_result = make_passed_scenario_result()

    with when:
        event = formatter.format_scenario_passed_event(scenario_result)

    with then:
        assert event == {
            "event": "scenario_passed",
            "timestamp": format_ts(formatter.time_fn()),
            "scenario": {
                "id": scenario_result.scenario.unique_id,
                "subject": scenario_result.scenario.subject,
                "path": str(scenario_result.scenario.path),
                "lineno": scenario_result.scenario.lineno,
                "status": ScenarioStatus.PASSED.value,
                "elapsed": format_ts(scenario_result.elapsed),
                "skip_reason": None,
            }
        }


@scenario
def format_scenario_passed_event_with_rich_output():
    with given:
        formatter = make_json_formatter()
        scenario_result = make_passed_scenario_result(started_at=1.5, ended_at=2.0)
        rich_output = "passed scenario output"

    with when:
        event = formatter.format_scenario_passed_event(scenario_result, rich_output=rich_output)

    with then:
        assert event == {
            "event": "scenario_passed",
            "timestamp": format_ts(formatter.time_fn()),
            "scenario": {
                "id": scenario_result.scenario.unique_id,
                "subject": scenario_result.scenario.subject,
                "path": str(scenario_result.scenario.path),
                "lineno": scenario_result.scenario.lineno,
                "status": ScenarioStatus.PASSED.value,
                "elapsed": format_ts(scenario_result.elapsed),
                "skip_reason": None,
            },
            "rich_output": "passed scenario output"
        }


@scenario
def format_scenario_failed_event():
    with given:
        formatter = make_json_formatter()
        scenario_result = make_failed_scenario_result()

    with when:
        event = formatter.format_scenario_failed_event(scenario_result)

    with then:
        assert event == {
            "event": "scenario_failed",
            "timestamp": format_ts(formatter.time_fn()),
            "scenario": {
                "id": scenario_result.scenario.unique_id,
                "subject": scenario_result.scenario.subject,
                "path": str(scenario_result.scenario.path),
                "lineno": scenario_result.scenario.lineno,
                "status": ScenarioStatus.FAILED.value,
                "elapsed": format_ts(scenario_result.elapsed),
                "skip_reason": None,
            }
        }


@scenario
def format_scenario_failed_event_with_rich_output():
    with given:
        formatter = make_json_formatter()
        scenario_result = make_failed_scenario_result(started_at=1.5, ended_at=2.0)
        rich_output = "failed scenario output"

    with when:
        event = formatter.format_scenario_failed_event(scenario_result, rich_output=rich_output)

    with then:
        assert event == {
            "event": "scenario_failed",
            "timestamp": format_ts(formatter.time_fn()),
            "scenario": {
                "id": scenario_result.scenario.unique_id,
                "subject": scenario_result.scenario.subject,
                "path": str(scenario_result.scenario.path),
                "lineno": scenario_result.scenario.lineno,
                "status": ScenarioStatus.FAILED.value,
                "elapsed": format_ts(scenario_result.elapsed),
                "skip_reason": None,
            },
            "rich_output": "failed scenario output"
        }
