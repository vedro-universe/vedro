from os import linesep
from unittest.mock import Mock, call

from vedro import catched, create_tmp_dir, given, scenario, then, when
from vedro.commands import Command, CommandArgumentParser
from vedro.commands.config_command import ConfigCommand
from vedro.commands.config_command._config_command import DEFAULT_CONFIG_TEMPLATE
from vedro.core import Config

from ._helpers import (
    create_read_only_dir,
    make_arg_parser,
    make_config_class,
    make_config_command,
    make_console,
)


@scenario("create config command")
def _():
    with given:
        config = Config
        arg_parser = CommandArgumentParser()

    with when:
        command = ConfigCommand(config, arg_parser)

    with then:
        assert isinstance(command, Command)


@scenario("run config init subcommand")
async def _():
    with given:
        config_class = make_config_class(project_dir_=create_tmp_dir())
        arg_parser_ = make_arg_parser(parse_args_result=Mock(subparser="init"))
        console_ = make_console()
        command = make_config_command(config_class, arg_parser_, console_)

    with when:
        result = await command.run()

    with then:
        assert result is None

        help_message = "Initialize a new vedro.cfg.py configuration file"
        assert arg_parser_.mock_calls == [
            call.add_subparsers(dest="subparser"),
            call.add_subparsers().add_parser("init", help=help_message),
            call.parse_args(),
        ]

        assert console_.mock_calls == [
            call.print("✔ Configuration file 'vedro.cfg.py' created successfully", style="green")
        ]


@scenario("run config init when file exists and empty")
async def _():
    with given:
        tmp_dir = create_tmp_dir()
        config_file = tmp_dir / "vedro.cfg.py"
        config_file.write_text("")  # empty file

        config_class = make_config_class(project_dir_=tmp_dir)
        arg_parser_ = make_arg_parser(parse_args_result=Mock(subparser="init"))
        console_ = make_console()
        command = make_config_command(config_class, arg_parser_, console_)

    with when:
        result = await command.run()

    with then:
        assert result is None

        # Empty file should be overwritten with template
        assert config_file.exists()
        assert config_file.read_text() == DEFAULT_CONFIG_TEMPLATE

        assert console_.mock_calls == [
            call.print("✔ Configuration file 'vedro.cfg.py' created successfully", style="green")
        ]


@scenario("try to run config init when file exists and not empty")
async def _():
    with given:
        tmp_dir = create_tmp_dir()
        config_file = tmp_dir / "vedro.cfg.py"
        config_file.write_text(original_content := linesep.join([
            "import vedro",
            "class Config(vedro.Config):",
            "    pass"
        ]))

        config_class = make_config_class(project_dir_=tmp_dir)
        arg_parser_ = make_arg_parser(parse_args_result=Mock(subparser="init"))
        console_ = make_console()
        command = make_config_command(config_class, arg_parser_, console_)

    with when, catched() as exc_info:
        await command.run()

    with then:
        assert exc_info.type == SystemExit

        # File content should remain unchanged
        assert config_file.read_text() == original_content

        assert console_.mock_calls == [
            call.print("✗ Configuration file 'vedro.cfg.py' already exists and is not empty",
                       style="red")
        ]


@scenario("try to run config init when file is not writable")
async def _():
    with given:
        tmp_dir = create_read_only_dir()

        config_class = make_config_class(project_dir_=tmp_dir)
        arg_parser_ = make_arg_parser(parse_args_result=Mock(subparser="init"))
        console_ = make_console()
        command = make_config_command(config_class, arg_parser_, console_)

    with when, catched() as exc_info:
        await command.run()

    with then:
        assert exc_info.type == SystemExit

        config_path = tmp_dir / "vedro.cfg.py"
        assert console_.mock_calls == [
            call.print(f"✗ Could not write to file '{config_path}'",
                       style="red"),
            call.print_exception(),
        ]


@scenario("try to run config without subcommand")
async def _():
    with given:
        config_class = make_config_class(project_dir_=create_tmp_dir())
        arg_parser_ = make_arg_parser()
        console_ = make_console()
        command = make_config_command(config_class, arg_parser_, console_)

    with when:
        await command.run()

    with then:
        assert arg_parser_.mock_calls[-1] == call.exit()
        assert console_.mock_calls == []
