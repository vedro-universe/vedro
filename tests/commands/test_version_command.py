from unittest.mock import Mock, call

import pytest
from baby_steps import given, then, when
from rich.console import Console
from rich.style import Style

import vedro
from vedro.commands._cmd_arg_parser import CommandArgumentParser
from vedro.commands._command import Command
from vedro.commands._version_command import VersionCommand
from vedro.core import Config


@pytest.fixture()
def arg_parser_() -> CommandArgumentParser:
    return Mock(CommandArgumentParser)


@pytest.fixture()
def console_() -> Console:
    return Mock(Console)


def test_inheritance():
    with given:
        config = Config
        arg_parser = CommandArgumentParser()

    with when:
        command = VersionCommand(config, arg_parser)

    with then:
        assert isinstance(command, Command)


@pytest.mark.asyncio
async def test_run(*, console_, arg_parser_: Mock):
    with given:
        command = VersionCommand(Config, arg_parser_, console_factory=lambda: console_)

    with when:
        result = await command.run()

    with then:
        assert result is None
        assert arg_parser_.mock_calls == [call.parse_args()]
        assert console_.mock_calls == [
            call.print(f"Vedro {vedro.__version__}", style=Style(color="blue"))
        ]
