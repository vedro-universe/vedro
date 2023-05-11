from baby_steps import given, then, when

from vedro.commands import Command, CommandArgumentParser
from vedro.commands.plugin_command import PluginCommand
from vedro.core import Config


def test_inheritance():
    with given:
        config = Config
        arg_parser = CommandArgumentParser()

    with when:
        command = PluginCommand(config, arg_parser)

    with then:
        assert isinstance(command, Command)
