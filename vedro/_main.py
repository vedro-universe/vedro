import os
import sys
from argparse import ArgumentParser, HelpFormatter
from functools import partial
from pathlib import Path
from typing import Type, cast

from ._config import Config
from .commands import CommandArgumentParser
from .commands.plugin_command import PluginCommand
from .commands.run_command import RunCommand
from .commands.version_command import VersionCommand
from .core import ConfigFileLoader


async def main() -> None:
    """
    Execute the main logic of the Vedro command-line interface.

    This function handles the parsing of command-line arguments, dynamically loads
    configuration files, and invokes the appropriate command based on the user's input.

    Steps include:
    - Parsing the project directory argument.
    - Validating the existence and type of the specified project directory.
    - Dynamically loading the configuration file.
    - Parsing the main command (run, version, plugin, etc.).
    - Executing the corresponding command logic.

    :raises FileNotFoundError: If the specified project directory does not exist.
    :raises NotADirectoryError: If the specified project directory path is not a directory.
    """
    # TODO: add argv parameter to main function in v2 to make it testable
    shadow_parser = ArgumentParser(add_help=False, allow_abbrev=False)
    shadow_parser.add_argument("--project-dir", type=Path, default=Path.cwd())
    shadow_args, _ = shadow_parser.parse_known_args()

    project_dir = shadow_args.project_dir.absolute()
    if not project_dir.exists():
        raise FileNotFoundError(f"Specified project directory '{project_dir}' does not exist")
    if not project_dir.is_dir():
        raise NotADirectoryError(f"Specified path '{project_dir}' is not a directory")
    os.chdir(project_dir)
    if str(project_dir) not in sys.path:
        sys.path.insert(0, str(project_dir))

    config_loader = ConfigFileLoader(Config)
    config_path = Path("vedro.cfg.py")
    config = cast(Type[Config], await config_loader.load(config_path))

    formatter = partial(HelpFormatter, max_help_position=30)
    arg_parser = ArgumentParser("vedro", formatter_class=formatter, add_help=False,
                                allow_abbrev=False, description="documentation: vedro.io/docs")

    commands = {"run", "version", "plugin"}
    arg_parser.add_argument("command", nargs="?", help=f"Command to run {{{', '.join(commands)}}}")
    args, unknown_args = arg_parser.parse_known_args()

    # backward compatibility
    # vedro <args> -> vedro run <args>
    help_args = {"-h", "--help"}
    cmd_aliases = commands | {"plugins"}
    if (args.command not in cmd_aliases) and (not help_args.intersection(set(unknown_args))):
        default_command = "run"
        sys.argv.insert(1, default_command)
        args.command = default_command

    arg_parser_factory = partial(CommandArgumentParser, formatter_class=formatter,
                                 allow_abbrev=False, add_help=True)

    if args.command == "run":
        parser = arg_parser_factory("vedro run")
        await RunCommand(config, parser).run()

    elif args.command == "version":
        parser = arg_parser_factory("vedro version")
        await VersionCommand(config, parser).run()

    elif args.command in ("plugin", "plugins"):
        parser = arg_parser_factory("vedro plugin")
        await PluginCommand(config, parser).run()

    else:
        arg_parser.print_help()
        arg_parser.exit()
