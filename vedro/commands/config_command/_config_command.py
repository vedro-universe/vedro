import sys
from typing import Any, Callable, Type

from rich.console import Console

from vedro import Config

from .._cmd_arg_parser import CommandArgumentParser
from .._command import Command

__all__ = ("ConfigCommand", "DEFAULT_CONFIG_TEMPLATE",)


DEFAULT_CONFIG_TEMPLATE = """
import vedro.plugins.director.rich
import vedro.plugins.skipper
from vedro.config import env

class Config(vedro.Config):
    class Plugins(vedro.Config.Plugins):
        class RichReporter(vedro.plugins.director.rich.RichReporter):
            enabled = True
            show_scenario_spinner = True
            show_full_diff = False

        class Skipper(vedro.plugins.skipper.Skipper):
            enabled = True
            forbid_only = env.bool("CI", default=False)
""".lstrip()


def make_console(**kwargs: Any) -> Console:
    """
    Create and configure a Rich Console instance.

    The console is used for outputting text in the terminal.

    :param kwargs: Additional keyword arguments to customize the Console.
    :return: A `Console` instance with specific configurations.
    """
    return Console(highlight=False, force_terminal=True, markup=False, soft_wrap=True,
                   file=sys.stdout, **kwargs)


class ConfigCommand(Command):
    """
    Implements the 'config' command for Vedro.

    This command manages Vedro configuration files, providing functionality to:
    - Initialize new configuration files with sensible defaults
    - Validate existing configurations (future functionality)
    """

    def __init__(self, config: Type[Config], arg_parser: CommandArgumentParser, *,
                 console_factory: Callable[[], Console] = make_console) -> None:
        """
        Initialize the ConfigCommand.

        :param config: The configuration class for Vedro.
        :param arg_parser: The argument parser for parsing command-line arguments.
        :param console_factory: A callable that returns a `Console` instance for output.
        """
        super().__init__(config, arg_parser)
        self._console = console_factory()

    async def run(self) -> None:
        """
        Execute the 'config' command.

        Parses the subcommand and executes the appropriate action:
        - 'init': Creates a new vedro.cfg.py configuration file
        - No subcommand: Displays help information
        """
        subparsers = self._arg_parser.add_subparsers(dest="subparser")

        subparsers.add_parser("init", help="Initialize a new vedro.cfg.py configuration file")

        args = self._arg_parser.parse_args()
        if args.subparser == "init":
            self._init_config()
        else:
            self._arg_parser.print_help()
            self._arg_parser.exit()

    def _init_config(self) -> None:
        """
        Initialize a new configuration file in the project directory.

        Creates a vedro.cfg.py file with default configuration settings including:
        - RichReporter plugin with sensible defaults
        - Skipper plugin with CI-aware configuration

        The method will:
        1. Check if a non-empty configuration file already exists
        2. Create the configuration file with default template
        3. Display success message with the created file path

        Exits with status code 1 if:
        - Configuration file already exists with content
        - Unable to write to the configuration file
        """
        config_path = self._config.project_dir / "vedro.cfg.py"

        try:
            content = config_path.read_text()
            if content.strip():
                message = "✗ Configuration file 'vedro.cfg.py' already exists and is not empty"
                self._console.print(message, style="red")
                sys.exit(1)
        except FileNotFoundError:
            # File doesn't exist, which is fine
            pass

        try:
            config_path.write_text(DEFAULT_CONFIG_TEMPLATE)
        except OSError:
            message = f"✗ Could not write to file '{config_path}'"
            self._console.print(message, style="red")
            self._console.print_exception()
            sys.exit(1)

        try:
            rel_path = config_path.relative_to(self._config.project_dir)
        except ValueError:  # pragma: no cover
            rel_path = config_path

        message = f"✔ Configuration file '{rel_path}' created successfully"
        self._console.print(message, style="green")
