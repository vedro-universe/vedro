from argparse import ArgumentParser, Namespace
from io import StringIO
from typing import Any, Optional
from unittest.mock import Mock, call

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
from vedro.core import Config, ConfigType, Dispatcher
from vedro.core.exc_info import TracebackFilter
from vedro.events import ArgParsedEvent, ArgParseEvent, ConfigLoadedEvent
from vedro.plugins.director import Director, DirectorPlugin
from vedro.plugins.director.json import JsonFormatter, JsonReporter, JsonReporterPlugin
from vedro.plugins.director.json._json_reporter import JsonFormatterFactory


def make_config() -> ConfigType:
    class TestConfig(Config):
        class Registry(Config.Registry):
            TracebackFilter = lambda modules: Mock(spec_set=TracebackFilter)  # noqa: E731
    return TestConfig


async def fire_config_loaded_event(dispatcher: Dispatcher,
                                   config: Optional[ConfigType] = None) -> None:
    if config is None:
        config = make_config()
    config_loaded_event = ConfigLoadedEvent(config.path, config)
    await dispatcher.fire(config_loaded_event)


async def fire_arg_parsed_event(dispatcher: Dispatcher) -> None:
    arg_parse_event = ArgParseEvent(ArgumentParser())
    await dispatcher.fire(arg_parse_event)

    arg_parsed_event = ArgParsedEvent(Namespace())
    await dispatcher.fire(arg_parsed_event)


def make_json_reporter(formatter_factory: JsonFormatterFactory) -> JsonReporterPlugin:
    class _JsonReporter(JsonReporter):
        class RichReporter(JsonReporter.RichReporter):
            enabled = False

    output = StringIO()
    reporter = JsonReporterPlugin(_JsonReporter, formatter_factory=formatter_factory,
                                  output=output)
    return reporter


def make_director_plugin(dispatcher: Dispatcher) -> DirectorPlugin:
    class _Director(Director):
        default_reporters = ["json"]

    director = DirectorPlugin(_Director)
    director.subscribe(dispatcher)

    return director


def make_formatter_mock(**kwargs: Any) -> JsonFormatter:
    return Mock(spec_set=JsonFormatter, **kwargs)


def make_formatted_event_mock(event_name: str = "<event>") -> Mock:
    return Mock(return_value={"event": event_name})


@scenario
async def trigger_startup_event():
    with given:
        make_director_plugin(dispatcher := make_dispatcher())

        formatter_ = make_formatter_mock(format_startup_event=make_formatted_event_mock())
        reporter = make_json_reporter(lambda tb_filter: formatter_)
        reporter.subscribe(dispatcher)

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
        make_director_plugin(dispatcher := make_dispatcher())

        formatter_ = make_formatter_mock(format_startup_event=make_formatted_event_mock())
        reporter = make_json_reporter(lambda tb_filter: formatter_)
        reporter.subscribe(dispatcher)

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
        make_director_plugin(dispatcher := make_dispatcher())

        formatter_ = make_formatter_mock(format_scenario_run_event=make_formatted_event_mock())
        reporter = make_json_reporter(lambda tb_filter: formatter_)
        reporter.subscribe(dispatcher)

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
        make_director_plugin(dispatcher := make_dispatcher())

        formatter_ = make_formatter_mock(format_scenario_passed_event=make_formatted_event_mock())
        reporter = make_json_reporter(lambda tb_filter: formatter_)
        reporter.subscribe(dispatcher)

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
        make_director_plugin(dispatcher := make_dispatcher())

        formatter_ = make_formatter_mock(format_scenario_failed_event=make_formatted_event_mock())
        reporter = make_json_reporter(lambda tb_filter: formatter_)
        reporter.subscribe(dispatcher)

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
        make_director_plugin(dispatcher := make_dispatcher())

        formatter_ = make_formatter_mock(format_scenario_skipped_event=make_formatted_event_mock())
        reporter = make_json_reporter(lambda tb_filter: formatter_)
        reporter.subscribe(dispatcher)

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
        make_director_plugin(dispatcher := make_dispatcher())

        formatter_ = make_formatter_mock(
            format_scenario_reported_event=make_formatted_event_mock()
        )
        reporter = make_json_reporter(lambda tb_filter: formatter_)
        reporter.subscribe(dispatcher)

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
        make_director_plugin(dispatcher := make_dispatcher())

        formatter_ = make_formatter_mock(format_cleanup_event=make_formatted_event_mock())
        reporter = make_json_reporter(lambda tb_filter: formatter_)
        reporter.subscribe(dispatcher)

        await fire_config_loaded_event(dispatcher)
        await fire_arg_parsed_event(dispatcher)

        cleanup_event = make_cleanup_event()

    with when:
        await dispatcher.fire(cleanup_event)

    with then:
        assert formatter_.mock_calls == [
            call.format_cleanup_event(cleanup_event.report, rich_output=None)
        ]
