from typing import Type
from unittest.mock import Mock

from rich.console import Console

from vedro.commands import CommandArgumentParser
from vedro.commands.version_command import VersionCommand
from vedro.core import Config

__all__ = ("make_version_command", "make_arg_parser", "make_console")


def make_arg_parser(parse_args_result: Mock = None) -> Mock:
    arg_parser_ = Mock(spec_set=CommandArgumentParser)

    if parse_args_result is None:
        parse_args_result = Mock(no_color=False)

    arg_parser_.parse_args.return_value = Mock(no_color=False)

    return arg_parser_


def make_console() -> Mock:
    return Mock(spec_set=Console)


def make_version_command(config_class: Type[Config],
                         arg_parser_: CommandArgumentParser,
                         console_: Console) -> VersionCommand:
    return VersionCommand(config_class, arg_parser_, console_factory=lambda: console_)
