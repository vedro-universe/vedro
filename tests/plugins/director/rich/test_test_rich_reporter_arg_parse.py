from argparse import ArgumentParser
from pathlib import Path
from unittest.mock import Mock

import pytest
from baby_steps import given, then, when

from vedro import Config
from vedro.core import Dispatcher
from vedro.events import ArgParseEvent, ConfigLoadedEvent
from vedro.plugins.director import DirectorPlugin, RichReporterPlugin
from vedro.plugins.director.rich.test_utils import console_, director, dispatcher, reporter

__all__ = ("dispatcher", "reporter", "director", "console_",)


@pytest.mark.asyncio
async def test_rich_reporter_arg_parse_event(*, dispatcher: Dispatcher, director: DirectorPlugin,
                                             reporter: RichReporterPlugin, console_: Mock):
    with given:
        await dispatcher.fire(ConfigLoadedEvent(Path(), Config))

        parser = ArgumentParser()
        event = ArgParseEvent(parser)

    with when:
        await dispatcher.fire(event)

    with then:
        assert console_.mock_calls == []
