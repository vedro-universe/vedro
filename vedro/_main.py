import sys
from argparse import ArgumentParser, HelpFormatter
from functools import partial
from pathlib import Path
from typing import Type, cast

from ._config import Config
from .commands import CommandArgumentParser, RunCommand
from .core import ConfigFileLoader


async def main() -> None:
    formatter = partial(HelpFormatter, max_help_position=30)
    config_path = Path("vedro.cfg.py")

    arg_parser = ArgumentParser("vedro", formatter_class=formatter,
                                add_help=False, allow_abbrev=False,
                                description="documentation: vedro.io/docs")

    config_loader = ConfigFileLoader(Config)
    config = cast(Type[Config], await config_loader.load(config_path))

    arg_parser.add_argument("command", nargs="?", help="Command to run {run, version, plugin}")
    args, unknown_args = arg_parser.parse_known_args()

    # backward compatibility
    # vedro <args> -> vedro run <args>
    help_args = {"-h", "--help"}
    if (args.command is None) and (not help_args.intersection(set(unknown_args))):
        default_command = "run"
        sys.argv.insert(1, default_command)
        args.command = default_command

    arg_parser_factory = partial(CommandArgumentParser, formatter_class=formatter,
                                 allow_abbrev=False, add_help=True)

    if args.command == "run":
        parser = arg_parser_factory("vedro run")
        await RunCommand(config, parser).run()
    else:
        arg_parser.print_help()
        arg_parser.exit()
