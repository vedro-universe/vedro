from argparse import ArgumentParser, Namespace
from io import StringIO
from typing import Optional, Tuple
from unittest.mock import Mock

from vedro.core import Config, ConfigType, Dispatcher
from vedro.core.exc_info import TracebackFilter
from vedro.events import ArgParsedEvent, ArgParseEvent, ConfigLoadedEvent
from vedro.plugins.director import Director, DirectorPlugin
from vedro.plugins.director.json import JsonFormatter, JsonReporter, JsonReporterPlugin
from vedro.plugins.director.json._json_reporter import JsonFormatterFactory

__all__ = ("make_config", "fire_config_loaded_event", "fire_arg_parsed_event",
           "make_json_reporter", "make_director_plugin", "setup_json_reporter",)


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

    reporter = JsonReporterPlugin(_JsonReporter, output=StringIO(),
                                  formatter_factory=lambda tb_filter: formatter_factory)
    return reporter


def make_director_plugin(dispatcher: Dispatcher) -> DirectorPlugin:
    class _Director(Director):
        default_reporters = ["json"]

    director = DirectorPlugin(_Director)
    director.subscribe(dispatcher)

    return director


def setup_json_reporter(dispatcher: Dispatcher, mocked_event: str
                        ) -> Tuple[JsonReporterPlugin, JsonFormatter]:
    make_director_plugin(dispatcher)

    formatter_ = Mock(spec_set=JsonFormatter)
    method_name = f"format_{mocked_event}_event"
    setattr(formatter_, method_name, Mock(return_value={"event": mocked_event}))

    reporter = make_json_reporter(formatter_)
    reporter.subscribe(dispatcher)

    return reporter, formatter_
