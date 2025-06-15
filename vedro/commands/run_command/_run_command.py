import inspect
import os
import warnings
from argparse import Namespace
from pathlib import Path
from typing import Callable, Type, Union

from vedro import Config
from vedro.core import Config as BaseConfig
from vedro.core import Dispatcher, MonotonicScenarioRunner
from vedro.events import (
    ArgParsedEvent,
    ArgParseEvent,
    CleanupEvent,
    ConfigLoadedEvent,
    StartupEvent,
)
from vedro.plugins.dry_runner import DryRunner

from .._cmd_arg_parser import CommandArgumentParser
from .._command import Command
from ._config_validator import ConfigValidator
from ._plugin_config_validator import PluginConfigValidator
from ._plugin_registrar import PluginRegistrar

__all__ = ("RunCommand",)

ConfigValidatorFactory = Union[
    Type[ConfigValidator],
    Callable[[Type[BaseConfig]], ConfigValidator]
]

PluginRegistrarFactory = Union[
    Type[PluginRegistrar],
    Callable[[], PluginRegistrar]
]


class RunCommand(Command):
    """
    Implements the 'run' command for Vedro.

    This command handles the lifecycle of running scenarios, including configuration
    validation, plugin registration, scenario discovery, execution, and reporting.
    """

    def __init__(self, config: Type[Config], arg_parser: CommandArgumentParser, *,
                 config_validator_factory: ConfigValidatorFactory = ConfigValidator,
                 plugin_registrar_factory: PluginRegistrarFactory = PluginRegistrar) -> None:
        """
        Initialize the RunCommand.

        :param config: The configuration class for Vedro.
        :param arg_parser: The argument parser for parsing command-line arguments.
        :param config_validator_factory: Factory for creating a `ConfigValidator` instance.
        :param plugin_registrar_factory: Factory for creating a `PluginRegistrar` instance.
        """
        super().__init__(config, arg_parser)
        self._config_validator = config_validator_factory(config)
        self._plugin_registrar = plugin_registrar_factory(
            plugin_config_validator_factory=lambda: PluginConfigValidator(
                validate_plugins_attrs=config.validate_plugins_configs  # type: ignore
            )
        )

    async def run(self) -> None:
        """
        Execute the 'run' command.

        This method validates the configuration, registers plugins, discovers scenarios,
        executes scenarios, and generates the report. It also fires various events during
        the lifecycle.

        :raises Exception: If a `SystemExit` exception is encountered during discovery.
        """
        # TODO: move config validation to somewhere else in v2
        # (e.g. to the ConfigLoader)
        self._config_validator.validate()  # Must be before ConfigLoadedEvent

        dispatcher = self._config.Registry.Dispatcher()
        self._plugin_registrar.register(self._config.Plugins.values(), dispatcher)

        await dispatcher.fire(ConfigLoadedEvent(self._config.path, self._config))

        args = await self._parse_args(dispatcher)
        start_dir = self._get_start_dir(args)

        discoverer = self._config.Registry.ScenarioDiscoverer()

        kwargs = {}
        # Backward compatibility (to be removed in v2):
        signature = inspect.signature(discoverer.discover)
        if "project_dir" in signature.parameters:
            kwargs["project_dir"] = self._config.project_dir

        try:
            scenarios = await discoverer.discover(start_dir, **kwargs)
        except SystemExit as e:
            raise Exception(f"SystemExit({e.code}) ⬆")

        scheduler = self._config.Registry.ScenarioScheduler(scenarios)
        await dispatcher.fire(StartupEvent(scheduler))

        runner = self._config.Registry.ScenarioRunner()
        if not isinstance(runner, (MonotonicScenarioRunner, DryRunner)):
            warnings.warn("Deprecated: custom runners will be removed in v2.0", DeprecationWarning)
        report = await runner.run(scheduler)

        await dispatcher.fire(CleanupEvent(report))

    async def _parse_args(self, dispatcher: Dispatcher) -> Namespace:
        """
        Parse command-line arguments and fire corresponding dispatcher events.

        Adds the `--project-dir` argument, fires the `ArgParseEvent`, parses
        the arguments, and then fires the `ArgParsedEvent`.

        :param dispatcher: The dispatcher to fire events.
        :return: The parsed arguments as a `Namespace` object.
        """

        # Avoid unrecognized arguments error
        help_message = ("Specify the root directory of the project, used as a reference point for "
                        "relative paths and file operations. "
                        "Defaults to the directory from which the command is executed.")
        self._arg_parser.add_argument("--project-dir", type=Path,
                                      default=self._config.project_dir,
                                      help=help_message)

        # https://github.com/python/cpython/issues/95073
        self._arg_parser.remove_help_action()
        await dispatcher.fire(ArgParseEvent(self._arg_parser))
        self._arg_parser.add_help_action()

        args = self._arg_parser.parse_args()
        await dispatcher.fire(ArgParsedEvent(args))

        return args

    def _get_start_dir(self, args: Namespace) -> Path:
        """
        Determine the starting directory for discovering scenarios.

        Resolves the starting directory based on the parsed arguments, ensuring
        it is a valid directory inside the project directory.

        :param args: Parsed command-line arguments.
        :return: The resolved starting directory.
        :raises ValueError: If the starting directory is outside the project directory.
        """
        file_or_dir = getattr(args, "file_or_dir", [])
        # Note: `args.file_or_dir` is an argument that is registered by the core Skipper plugin.
        # This introduces a dependency on the Skipper plugin's implementation,
        # violating best practices, as the higher-level RunCommand component directly relies
        # on a lower-level plugin.
        # TODO: Fix this in v2.0 by introducing a more generic mechanism for passing arguments
        if not file_or_dir:
            return Path(self._config.default_scenarios_dir).resolve()

        common_path = os.path.commonpath([self._normalize_path(x) for x in file_or_dir])
        start_dir = Path(common_path).resolve()
        if not start_dir.is_dir():
            start_dir = start_dir.parent

        try:
            start_dir.relative_to(self._config.project_dir)
        except ValueError:
            raise ValueError(
                f"The start directory '{start_dir}' must be inside the project directory "
                f"('{self._config.project_dir}')"
            )

        return start_dir

    def _normalize_path(self, file_or_dir: str) -> str:
        """
        Normalize the provided path and handle backward compatibility.

        Ensures the path is absolute and adjusts it based on legacy rules if necessary.

        :param file_or_dir: The path to normalize.
        :return: The normalized absolute path.
        """
        path = os.path.normpath(file_or_dir)
        if os.path.isabs(path):
            return path

        # Backward compatibility (to be removed in v2):
        # Only prepend "scenarios/" if:
        # 1) The default_scenarios_dir is exactly <project_dir>/scenarios
        # 2) The original path does not exist, but "scenarios/<path>" does
        scenarios_dir = Path(self._config.default_scenarios_dir).resolve()
        if scenarios_dir == self._config.project_dir / "scenarios":
            updated_path = os.path.join("scenarios/", path)
            if not os.path.exists(path) and os.path.exists(updated_path):
                return os.path.abspath(updated_path)

        return os.path.abspath(path)
