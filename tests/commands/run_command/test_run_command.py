from pathlib import Path

from baby_steps import given, then, when
from pytest import raises

import vedro
from vedro.commands.run_command import RunCommand
from vedro.core import Config, Dispatcher, Factory

from ._utils import ArgumentParser, arg_parser, create_scenario, tmp_dir

__all__ = ("tmp_dir", "arg_parser")  # fixtures


class CustomConfig(Config):
    validate_plugins_configs = False

    class Registry(vedro.Config.Registry):
        Dispatcher = Factory[Dispatcher](Dispatcher)

    class Plugins(Config.Plugins):
        class Terminator(vedro.Config.Plugins.Terminator):
            pass


async def test_run_command_without_scenarios(tmp_dir: Path, arg_parser: ArgumentParser):
    with given:
        class CustomConfigProject(CustomConfig):
            project_dir = tmp_dir

        command = RunCommand(CustomConfigProject, arg_parser)

    with when, raises(BaseException) as exc:
        await command.run()

    with then:
        assert exc.type is SystemExit
        assert str(exc.value) == "1"


async def test_run_command_with_scenarios(tmp_dir: Path, arg_parser: ArgumentParser):
    with given:
        class CustomConfigProject(CustomConfig):
            project_dir = tmp_dir

        command = RunCommand(CustomConfigProject, arg_parser)
        create_scenario(tmp_dir, "scenario.py")

    with when, raises(BaseException) as exc:
        await command.run()

    with then:
        assert exc.type is SystemExit
        assert str(exc.value) == "0"
