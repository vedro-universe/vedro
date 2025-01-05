from pathlib import Path

import pytest
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


async def test_run_command_with_invalid_type_scenario_dir(arg_parser: ArgumentParser):
    with given:
        class CustomScenarioDir(CustomConfig):
            default_scenarios_dir = None
        command = RunCommand(CustomScenarioDir, arg_parser)

    with when, raises(BaseException) as exc:
        await command.run()

    with then:
        assert exc.type is TypeError
        assert "default_scenarios_dir" in str(exc.value)
        assert "to be a Path" in str(exc.value)


async def test_run_command_with_nonexistent_scenario_dir(arg_parser: ArgumentParser):
    with given:
        class CustomScenarioDir(CustomConfig):
            default_scenarios_dir = "nonexisting/"
        command = RunCommand(CustomScenarioDir, arg_parser)

    with when, raises(BaseException) as exc:
        await command.run()

    with then:
        assert exc.type is FileNotFoundError
        assert "default_scenarios_dir" in str(exc.value)
        assert "does not exist" in str(exc.value)


async def test_run_command_with_non_directory_scenario_dir(tmp_dir: Path,
                                                           arg_parser: ArgumentParser):
    with given:
        existing_file = tmp_dir / "scenario.py"
        existing_file.touch()

        class CustomScenarioDir(CustomConfig):
            default_scenarios_dir = existing_file
        command = RunCommand(CustomScenarioDir, arg_parser)

    with when, raises(BaseException) as exc:
        await command.run()

    with then:
        assert exc.type is NotADirectoryError
        assert "default_scenarios_dir" in str(exc.value)
        assert "is not a directory" in str(exc.value)


@pytest.mark.usefixtures(tmp_dir.__name__)
async def test_run_command_with_scenario_dir_outside_project_dir(arg_parser: ArgumentParser):
    with given:
        class CustomScenarioDir(CustomConfig):
            default_scenarios_dir = "/tmp"
        command = RunCommand(CustomScenarioDir, arg_parser)

    with when, raises(BaseException) as exc:
        await command.run()

    with then:
        assert exc.type is ValueError
        assert "default_scenarios_dir" in str(exc.value)
        assert "must be inside project directory" in str(exc.value)


async def test_run_command_without_scenarios(arg_parser: ArgumentParser):
    with given:
        command = RunCommand(CustomConfig, arg_parser)

    with when, raises(BaseException) as exc:
        await command.run()

    with then:
        assert exc.type is SystemExit
        assert str(exc.value) == "1"


@pytest.mark.usefixtures(tmp_dir.__name__)
async def test_run_command_with_no_scenarios(arg_parser: ArgumentParser):
    with given:
        command = RunCommand(CustomConfig, arg_parser)

    with when, raises(BaseException) as exc:
        await command.run()

    with then:
        assert exc.type is SystemExit
        assert str(exc.value) == "1"


async def test_run_command_with_scenarios(tmp_dir: Path, arg_parser: ArgumentParser):
    with given:
        command = RunCommand(CustomConfig, arg_parser)
        create_scenario(tmp_dir, "scenario.py")

    with when, raises(BaseException) as exc:
        await command.run()

    with then:
        assert exc.type is SystemExit
        assert str(exc.value) == "0"


async def test_run_command_validate_plugin(tmp_dir: Path, arg_parser: ArgumentParser):
    with given:
        class ValidConfig(CustomConfig):
            validate_plugins_configs = True

            class Plugins(Config.Plugins):
                class Terminator(vedro.Config.Plugins.Terminator):
                    enabled = True

        command = RunCommand(ValidConfig, arg_parser)
        create_scenario(tmp_dir, "scenario.py")

    with when, raises(BaseException) as exc:
        await command.run()

    with then:
        assert exc.type is SystemExit
        assert str(exc.value) == "0"


@pytest.mark.usefixtures(tmp_dir.__name__)
async def test_run_command_validate_plugin_error(arg_parser: ArgumentParser):
    with given:
        class InvalidConfig(CustomConfig):
            validate_plugins_configs = True

            class Plugins(Config.Plugins):
                class Terminator(vedro.Config.Plugins.Terminator):
                    enabled = True
                    nonexisting = "nonexisting"

        command = RunCommand(InvalidConfig, arg_parser)

    with when, raises(BaseException) as exc:
        await command.run()

    with then:
        assert exc.type is AttributeError
        assert str(exc.value) == (
            "Terminator configuration contains unknown attributes: nonexisting"
        )
