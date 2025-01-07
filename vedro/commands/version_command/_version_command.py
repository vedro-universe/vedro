from typing import Callable, Type

from rich.console import Console
from rich.style import Style

import vedro
from vedro import Config

from .._cmd_arg_parser import CommandArgumentParser
from .._command import Command

__all__ = ("VersionCommand",)


def make_console() -> Console:
    """
    Create and configure a Rich Console instance.

    The console is used for outputting text in the terminal.

    :return: A `Console` instance with specific configurations.
    """
    return Console(highlight=False, force_terminal=True, markup=False, soft_wrap=True)


class VersionCommand(Command):
    """
    Implements the 'version' command for Vedro.

    This command outputs the current version of Vedro to the console.
    """

    def __init__(self, config: Type[Config], arg_parser: CommandArgumentParser, *,
                 console_factory: Callable[[], Console] = make_console) -> None:
        """
        Initialize the VersionCommand.

        :param config: The configuration class for Vedro.
        :param arg_parser: The argument parser for parsing command-line arguments.
        :param console_factory: A callable that returns a `Console` instance for output.
        """
        super().__init__(config, arg_parser)
        self._console = console_factory()

    async def run(self) -> None:
        """
        Execute the 'version' command.

        This method parses the command-line arguments and outputs the current version
        of Vedro to the console.
        """
        self._arg_parser.parse_args()
        self._console.print(f"Vedro {vedro.__version__}", style=Style(color="blue"))
