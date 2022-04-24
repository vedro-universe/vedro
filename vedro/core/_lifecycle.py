import os
from argparse import HelpFormatter
from functools import partial
from pathlib import Path
from typing import Tuple

from ..events import ArgParsedEvent, ArgParseEvent, CleanupEvent, ConfigLoadedEvent, StartupEvent
from ._arg_parser import ArgumentParser
from ._config_loader import ConfigLoader, ConfigType
from ._dispatcher import Dispatcher
from ._plugin import Plugin
from ._report import Report
from ._runner import Runner
from ._scenario_discoverer import ScenarioDiscoverer

__all__ = ("Lifecycle",)


class Lifecycle:
    def __init__(self,
                 dispatcher: Dispatcher,
                 discoverer: ScenarioDiscoverer,
                 runner: Runner,
                 config_loader: ConfigLoader) -> None:
        self._dispatcher = dispatcher
        self._discoverer = discoverer
        self._runner = runner
        self._config_loader = config_loader

    async def _load_config(self, filename: Path) -> Tuple[Path, ConfigType]:
        parser = ArgumentParser(add_help=False)
        parser.add_argument("--config", default=filename, type=Path)

        args, _ = parser.parse_known_args()
        if args.config != filename:
            assert args.config.exists(), f"'{args.config}' does not exist"

        config = await self._config_loader.load(args.config)
        return args.config, config

    async def start(self) -> Report:
        formatter = partial(HelpFormatter, max_help_position=30)
        default_config = Path("vedro.cfg.py")

        arg_parser = ArgumentParser("vedro", formatter_class=formatter, add_help=False,
                                    description="documentation: vedro.io/docs")
        arg_parser.add_argument("--config", default=default_config, type=Path,
                                help=f"Config path (default: {default_config})")
        arg_parser.add_argument("-h", "--help",
                                action="help", help="Show this help message and exit")

        config_path, config = await self._load_config(default_config)
        for _, section in config.Plugins.items():
            assert issubclass(section.plugin, Plugin)
            assert section.plugin != Plugin
            if section.enabled:
                plugin = section.plugin(config=section)
                self._dispatcher.register(plugin)
        await self._dispatcher.fire(ConfigLoadedEvent(config_path, config))

        subparsers = arg_parser.add_subparsers(dest="subparser")
        arg_parser_run = subparsers.add_parser("run", add_help=False,
                                               description="documentation: vedro.io/docs",
                                               help="Run scenarios. "
                                                    "Type 'vedro run --help' for more info")
        arg_parser.set_default_subparser("run")

        await self._dispatcher.fire(ArgParseEvent(arg_parser_run))
        arg_parser_run.add_argument("--reruns", type=int, default=0,
                                    help="Number of times to rerun failed scenarios (default: 0)")
        arg_parser_run.add_argument("--config", default=default_config, type=Path,
                                    help=f"Config path (default: {default_config})")
        arg_parser_run.add_argument("-h", "--help",
                                    action="help", help="Show this help message and exit")

        args = arg_parser.parse_args()
        await self._dispatcher.fire(ArgParsedEvent(args))

        start_dir = os.path.relpath(Path("scenarios"))
        scenarios = await self._discoverer.discover(Path(start_dir))
        await self._dispatcher.fire(StartupEvent(scenarios))

        report = await self._runner.run(scenarios, reruns=args.reruns)

        await self._dispatcher.fire(CleanupEvent(report))

        return report

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        return (f"{cls_name}({self._dispatcher!r}, {self._discoverer!r}, "
                f"{self._runner!r}, {self._config_loader!r})")
