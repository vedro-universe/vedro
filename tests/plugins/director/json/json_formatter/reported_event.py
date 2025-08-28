from traceback import extract_tb

from vedro import given, scenario, then, when
from vedro._test_utils import (
    make_failed_scenario_result,
    make_passed_step_result,
    make_step_result,
)
from vedro.core import AggregatedResult, ScenarioStatus, StepStatus
from vedro.core.exc_info import TracebackFilter

from ._helpers import format_ts, make_json_formatter
from ._tb_helpers import execute_and_capture_exception, generate_call_chain_modules


@scenario
def format_scenario_reported_event():
    with given:
        formatter = make_json_formatter()
        scenario_result = make_failed_scenario_result()
        aggregated_result = AggregatedResult.from_existing(scenario_result, [scenario_result])

    with when:
        event = formatter.format_scenario_reported_event(aggregated_result)

    with then:
        assert event == {
            "event": "scenario_reported",
            "timestamp": format_ts(formatter.time_fn()),
            "scenario": {
                "id": aggregated_result.scenario.unique_id,
                "subject": aggregated_result.scenario.subject,
                "path": str(aggregated_result.scenario.path),
                "lineno": aggregated_result.scenario.lineno,
                "status": ScenarioStatus.FAILED.value,
                "elapsed": format_ts(aggregated_result.elapsed),
                "skip_reason": None,
            },
            "steps": [],
        }


@scenario
def format_scenario_reported_event_with_steps():
    with given:
        formatter = make_json_formatter(TracebackFilter(modules=[]))

        scenario_result = make_failed_scenario_result()

        passed_step_result = make_passed_step_result()
        scenario_result.add_step_result(passed_step_result)

        tmp_dir = generate_call_chain_modules([("main.py", "main")])
        exc_info = execute_and_capture_exception(tmp_dir / "main.py", "main")
        failed_step_result = make_step_result(status=StepStatus.FAILED).set_exc_info(exc_info)
        scenario_result.add_step_result(failed_step_result)

        aggregated_result = AggregatedResult.from_existing(scenario_result, [scenario_result])

    with when:
        event = formatter.format_scenario_reported_event(aggregated_result)

    with then:
        last_frame = extract_tb(exc_info.traceback)[-1]
        assert event == {
            "event": "scenario_reported",
            "timestamp": format_ts(formatter.time_fn()),
            "scenario": {
                "id": aggregated_result.scenario.unique_id,
                "subject": aggregated_result.scenario.subject,
                "path": str(aggregated_result.scenario.path),
                "lineno": aggregated_result.scenario.lineno,
                "status": ScenarioStatus.FAILED.value,
                "elapsed": format_ts(aggregated_result.elapsed),
                "skip_reason": None,
            },
            "steps": [
                {
                    "name": passed_step_result.step.name,
                    "status": passed_step_result.status.value,
                    "elapsed": format_ts(passed_step_result.elapsed),
                    "error": None,
                },
                {
                    "name": failed_step_result.step.name,
                    "status": failed_step_result.status.value,
                    "elapsed": format_ts(failed_step_result.elapsed),
                    "error": {
                        "type": "ZeroDivisionError",
                        "message": "division by zero",
                        "file": last_frame.filename,
                        "lineno": last_frame.lineno,
                    },
                }
            ],
        }


@scenario
def format_scenario_reported_event_with_rich_output():
    with given:
        formatter = make_json_formatter()
        scenario_result = make_failed_scenario_result()
        aggregated_result = AggregatedResult.from_existing(scenario_result, [scenario_result])
        rich_output = "reported scenario output"

    with when:
        event = formatter.format_scenario_reported_event(aggregated_result,
                                                         rich_output=rich_output)

    with then:
        assert event == {
            "event": "scenario_reported",
            "timestamp": format_ts(formatter.time_fn()),
            "scenario": {
                "id": aggregated_result.scenario.unique_id,
                "subject": aggregated_result.scenario.subject,
                "path": str(aggregated_result.scenario.path),
                "lineno": aggregated_result.scenario.lineno,
                "status": ScenarioStatus.FAILED.value,
                "elapsed": format_ts(aggregated_result.elapsed),
                "skip_reason": None,
            },
            "steps": [],
            "rich_output": rich_output
        }
