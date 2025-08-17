import inspect
import os
import warnings
from argparse import Namespace
from pathlib import Path
from typing import Callable, Type, Union

from vedro import Config
from vedro.core import Config as BaseConfig
from vedro.core import Dispatcher, MonotonicScenarioRunner
from vedro.core.output_capturer import OutputCapturer
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
    Implements the 'run' command for the Vedro testing framework.

    This command orchestrates the complete test execution lifecycle including:
    - Configuration validation
    - Plugin registration
    - Test scenario discovery
    - Test execution
    - Report generation
    """

    def __init__(self, config: Type[Config], arg_parser: CommandArgumentParser, *,
                 config_validator_factory: ConfigValidatorFactory = ConfigValidator,
                 plugin_registrar_factory: PluginRegistrarFactory = PluginRegistrar) -> None:
        """
        Initialize the RunCommand.

        :param config: The Vedro configuration class.
        :param arg_parser: Command-line argument parser.
        :param config_validator_factory: Factory for creating a ConfigValidator instance.
        :param plugin_registrar_factory: Factory for creating a PluginRegistrar instance.
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
        Execute the 'run' command lifecycle.

        Performs the following steps:
        1. Validates configuration
        2. Registers plugins with the dispatcher
        3. Fires ConfigLoadedEvent
        4. Parses command-line arguments
        5. Discovers test scenarios
        6. Executes scenarios with output capturing
        7. Generates and processes the test report

        :raises Exception: If a SystemExit is raised during scenario discovery.
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

        output_capturer = OutputCapturer(args.capture_output, args.capture_limit)
        with OutputCapturer().capture() as _:
            scheduler = self._config.Registry.ScenarioScheduler(scenarios)
            await dispatcher.fire(StartupEvent(scheduler))

            runner = self._config.Registry.ScenarioRunner()
            if not isinstance(runner, (MonotonicScenarioRunner, DryRunner)):
                # TODO: In v2 add --dry-run argument to RunCommand
                warnings.warn("Deprecated: custom runners will be removed in v2.0", DeprecationWarning)
            report = await runner.run(scheduler, output_capturer=output_capturer)

            await dispatcher.fire(CleanupEvent(report))
        # In v2 RunCommand will handle report.interrupted and exit codes itself.
        # At that point, captured output should also be added to the Report.

    async def _parse_args(self, dispatcher: Dispatcher) -> Namespace:
        """
        Parse command-line arguments and fire corresponding events.

        Adds command-line arguments including:
        - --project-dir: Root directory of the project
        - --capture-output/-C: Enable output capturing
        - --capture-limit: Maximum bytes to capture

        :param dispatcher: Event dispatcher for firing ArgParseEvent and ArgParsedEvent.
        :return: Parsed arguments as a Namespace object.
        """
        # Avoid unrecognized arguments error
        help_message = ("Specify the root directory of the project, used as a reference point for "
                        "relative paths and file operations. "
                        "Defaults to the directory from which the command is executed.")
        self._arg_parser.add_argument("--project-dir", type=Path,
                                      default=self._config.project_dir,
                                      help=help_message)

        self._arg_parser.add_argument("--capture-output", "-C", action="store_true", default=False,
                                      help="Capture stdout/stderr from scenarios and steps")
        self._arg_parser.add_argument("--capture-limit", type=int, default=1 * 1024,
                                      help="Max bytes to capture (default: 1KB, 0 for unlimited)")

        # https://github.com/python/cpython/issues/95073
        self._arg_parser.remove_help_action()
        await dispatcher.fire(ArgParseEvent(self._arg_parser))
        self._arg_parser.add_help_action()

        args = self._arg_parser.parse_args()
        await dispatcher.fire(ArgParsedEvent(args))

        return args

    def _get_start_dir(self, args: Namespace) -> Path:
        """
        Determine the starting directory for scenario discovery.

        Resolves the starting directory based on command-line arguments,
        ensuring it exists within the project directory boundaries.

        :param args: Parsed command-line arguments containing file_or_dir paths.
        :return: Resolved absolute path to the starting directory.
        :raises ValueError: If the resolved directory is outside the project directory.
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
        Normalize a file or directory path to an absolute path.

        Handles backward compatibility by prepending "scenarios/" when:
        1. The default_scenarios_dir is <project_dir>/scenarios
        2. The original path doesn't exist but "scenarios/<path>" does

        :param file_or_dir: Path string to normalize (relative or absolute).
        :return: Normalized absolute path string.
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
