from unittest.mock import Mock, call

from rich.style import Style

import vedro
from vedro import given, scenario, then, when
from vedro.commands import Command, CommandArgumentParser
from vedro.commands.version_command import VersionCommand
from vedro.core import Config

from ._helpers import make_arg_parser, make_console, make_version_command


@scenario("create version command")
def _():
    with given:
        config = Config
        arg_parser = CommandArgumentParser()

    with when:
        command = VersionCommand(config, arg_parser)

    with then:
        assert isinstance(command, Command)


@scenario("run version command")
async def _():
    with given:
        arg_parser_ = make_arg_parser()
        console_ = make_console()
        command = make_version_command(Config, arg_parser_, console_)

    with when:
        result = await command.run()

    with then:
        assert result is None

        assert arg_parser_.mock_calls == [
            call.add_argument("--no-color", action="store_true", help="Disable colored output"),
            call.parse_args(),
        ]

        assert console_.mock_calls == [
            call.print(f"Vedro {vedro.__version__}", style=Style(color="blue"))
        ]


@scenario("run version command with no color option")
async def _():
    with given:
        arg_parser_ = make_arg_parser(parse_args_result=Mock(no_color=True))
        console_ = make_console()
        command = make_version_command(Config, arg_parser_, console_)

    with when:
        result = await command.run()

    with then:
        assert result is None

        assert arg_parser_.mock_calls == [
            call.add_argument("--no-color", action="store_true", help="Disable colored output"),
            call.parse_args(),
        ]

        assert console_.mock_calls == [
            call.print(f"Vedro {vedro.__version__}", style=Style(color="blue"))
        ]
