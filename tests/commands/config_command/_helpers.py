from pathlib import Path
from typing import Any, Optional, Type
from unittest.mock import Mock

from rich.console import Console

from vedro import create_tmp_dir, defer
from vedro.commands import CommandArgumentParser
from vedro.commands.config_command import ConfigCommand
from vedro.core import Config

__all__ = ("make_config_command", "make_arg_parser", "make_console", "make_config_class",
           "create_read_only_dir",)


def make_arg_parser(parse_args_result: Optional[Any] = None) -> Mock:
    arg_parser = Mock(spec_set=CommandArgumentParser)

    if parse_args_result is not None:
        arg_parser.parse_args.return_value = parse_args_result

    return arg_parser


def make_console() -> Mock:
    return Mock(spec_set=Console)


def make_config_class(project_dir_: Path) -> Type[Config]:
    class CustomConfigProject(Config):
        project_dir = project_dir_

    return CustomConfigProject


def make_config_command(config_class: Type[Config],
                        arg_parser: CommandArgumentParser,
                        console: Console) -> ConfigCommand:
    return ConfigCommand(config_class, arg_parser, console_factory=lambda: console)


def create_read_only_dir() -> Path:
    tmp_dir = create_tmp_dir()
    tmp_dir.chmod(0o555)
    defer(tmp_dir.chmod, 0o755)
    return tmp_dir
