from unittest.mock import call

from vedro import given, scenario, then, when
from vedro._test_utils import (
    make_cleanup_event,
    make_dispatcher,
    make_scenario_failed_event,
    make_scenario_passed_event,
    make_scenario_reported_event,
    make_scenario_run_event,
    make_scenario_scheduler,
    make_scenario_skipped_event,
    make_startup_event,
    make_vscenario,
)

from ._helpers import fire_arg_parsed_event, fire_config_loaded_event, setup_json_reporter


@scenario
async def trigger_startup_event():
    with given:
        dispatcher = make_dispatcher()
        reporter, formatter_ = setup_json_reporter(dispatcher, mocked_event="startup")

        await fire_config_loaded_event(dispatcher)
        await fire_arg_parsed_event(dispatcher)

        startup_event = make_startup_event()

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert formatter_.mock_calls == [
            call.format_startup_event(0, 0, 0, rich_output=None)
        ]


@scenario
async def trigger_startup_event_with_scheduled():
    with given:
        dispatcher = make_dispatcher()
        reporter, formatter_ = setup_json_reporter(dispatcher, mocked_event="startup")

        await fire_config_loaded_event(dispatcher)
        await fire_arg_parsed_event(dispatcher)

        scenarios = [make_vscenario() for _ in range(3)]
        scheduler = make_scenario_scheduler(scenarios)

        scheduler.ignore(scenarios[0])
        scenarios[-1].skip()
        startup_event = make_startup_event(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert formatter_.mock_calls == [
            call.format_startup_event(3, 2, 1, rich_output=None)
        ]


@scenario
async def trigger_scenario_run_event():
    with given:
        dispatcher = make_dispatcher()
        reporter, formatter_ = setup_json_reporter(dispatcher, mocked_event="scenario_run")

        await fire_config_loaded_event(dispatcher)
        await fire_arg_parsed_event(dispatcher)

        scenario_run_event = make_scenario_run_event()

    with when:
        await dispatcher.fire(scenario_run_event)

    with then:
        assert formatter_.mock_calls == [
            call.format_scenario_run_event(scenario_run_event.scenario_result)
        ]


@scenario
async def trigger_scenario_passed_event():
    with given:
        dispatcher = make_dispatcher()
        reporter, formatter_ = setup_json_reporter(dispatcher, mocked_event="scenario_passed")

        await fire_config_loaded_event(dispatcher)
        await fire_arg_parsed_event(dispatcher)

        scenario_passed_event = make_scenario_passed_event()

    with when:
        await dispatcher.fire(scenario_passed_event)

    with then:
        assert formatter_.mock_calls == [
            call.format_scenario_passed_event(scenario_passed_event.scenario_result)
        ]


@scenario
async def trigger_scenario_failed_event():
    with given:
        dispatcher = make_dispatcher()
        reporter, formatter_ = setup_json_reporter(dispatcher, mocked_event="scenario_failed")

        await fire_config_loaded_event(dispatcher)
        await fire_arg_parsed_event(dispatcher)

        scenario_failed_event = make_scenario_failed_event()

    with when:
        await dispatcher.fire(scenario_failed_event)

    with then:
        assert formatter_.mock_calls == [
            call.format_scenario_failed_event(scenario_failed_event.scenario_result)
        ]


@scenario
async def trigger_scenario_skipped_event():
    with given:
        dispatcher = make_dispatcher()
        reporter, formatter_ = setup_json_reporter(dispatcher, mocked_event="scenario_skipped")

        await fire_config_loaded_event(dispatcher)
        await fire_arg_parsed_event(dispatcher)

        scenario_skipped_event = make_scenario_skipped_event()

    with when:
        await dispatcher.fire(scenario_skipped_event)

    with then:
        assert formatter_.mock_calls == [
            call.format_scenario_skipped_event(scenario_skipped_event.scenario_result)
        ]


@scenario
async def trigger_scenario_reported_event():
    with given:
        dispatcher = make_dispatcher()
        reporter, formatter_ = setup_json_reporter(dispatcher, mocked_event="scenario_reported")

        await fire_config_loaded_event(dispatcher)
        await fire_arg_parsed_event(dispatcher)

        scenario_reported_event = make_scenario_reported_event()

    with when:
        await dispatcher.fire(scenario_reported_event)

    with then:
        assert formatter_.mock_calls == [
            call.format_scenario_reported_event(scenario_reported_event.aggregated_result,
                                                rich_output=None)
        ]


@scenario
async def trigger_cleanup_event():
    with given:
        dispatcher = make_dispatcher()
        reporter, formatter_ = setup_json_reporter(dispatcher, mocked_event="cleanup")

        await fire_config_loaded_event(dispatcher)
        await fire_arg_parsed_event(dispatcher)

        cleanup_event = make_cleanup_event()

    with when:
        await dispatcher.fire(cleanup_event)

    with then:
        assert formatter_.mock_calls == [
            call.format_cleanup_event(cleanup_event.report, rich_output=None)
        ]
