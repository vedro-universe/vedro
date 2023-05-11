from argparse import Namespace
from pathlib import Path
from unittest.mock import Mock

import pytest
from baby_steps import given, then, when
from pytest import raises

import vedro
from vedro.commands import CommandArgumentParser
from vedro.commands.run_command import RunCommand
from vedro.core import Config

from ._utils import create_scenario, tmp_dir

__all__ = ("tmp_dir",)  # fixtures


class CustomConfig(Config):
    class Registry(vedro.Config.Registry):
        pass

    class Plugins(Config.Plugins):
        class Terminator(vedro.Config.Plugins.Terminator):
            pass


@pytest.mark.asyncio
async def test_run_command_without_scenarios(tmp_dir: Path):
    with given:
        arg_parser = Mock(CommandArgumentParser, parse_known_args=(Namespace(), []))
        command = RunCommand(CustomConfig, arg_parser)

    with when, raises(BaseException) as exc:
        await command.run()

    with then:
        assert exc.type is SystemExit
        assert str(exc.value) == "1"


@pytest.mark.asyncio
async def test_run_command_with_scenarios(tmp_dir: Path):
    with given:
        create_scenario(tmp_dir, "scenario.py")

        arg_parser = Mock(CommandArgumentParser, parse_known_args=(Namespace(), []))
        command = RunCommand(CustomConfig, arg_parser)

    with when, raises(BaseException) as exc:
        await command.run()

    with then:
        assert exc.type is SystemExit
        assert str(exc.value) == "0"
