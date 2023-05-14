from typing import Callable, Type

from rich.console import Console
from rich.style import Style

import vedro
from vedro import Config

from .._cmd_arg_parser import CommandArgumentParser
from .._command import Command

__all__ = ("VersionCommand",)


def make_console() -> Console:
    return Console(highlight=False, force_terminal=True, markup=False, soft_wrap=True)


class VersionCommand(Command):
    def __init__(self, config: Type[Config], arg_parser: CommandArgumentParser, *,
                 console_factory: Callable[[], Console] = make_console) -> None:
        super().__init__(config, arg_parser)
        self._console = console_factory()

    async def run(self) -> None:
        self._arg_parser.parse_args()
        self._console.print(f"Vedro {vedro.__version__}", style=Style(color="blue"))
