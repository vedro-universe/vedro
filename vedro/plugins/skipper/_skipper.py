import os
from pathlib import Path
from typing import List, Optional, Set, Type, Union, final

from vedro.core import ConfigType, Dispatcher, Plugin, PluginConfig, VirtualScenario
from vedro.events import ArgParsedEvent, ArgParseEvent, ConfigLoadedEvent, StartupEvent

from ._discoverer import SelectiveScenarioDiscoverer as ScenarioDiscoverer

__all__ = ("Skipper", "SkipperPlugin",)


class _CompositePath:
    def __init__(self, file_path: str, cls_name: Optional[str], tmpl_idx: Optional[int]) -> None:
        self.file_path = file_path
        self.cls_name = cls_name
        self.tmpl_idx = tmpl_idx


@final
class SkipperPlugin(Plugin):
    def __init__(self, config: Type["Skipper"]) -> None:
        super().__init__(config)
        self._global_config: Union[ConfigType, None] = None
        self._project_dir: Union[Path, None] = None
        self._default_scenarios_dir: Union[Path, None] = None
        self._subject: Union[str, None] = None
        self._selected: List[_CompositePath] = []
        self._deselected: List[_CompositePath] = []
        self._forbid_only = config.forbid_only
        self._exp_selective_discoverer = config.exp_selective_discoverer

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ConfigLoadedEvent, self.on_config_loaded) \
                  .listen(ArgParseEvent, self.on_arg_parse) \
                  .listen(ArgParsedEvent, self.on_arg_parsed) \
                  .listen(StartupEvent, self.on_startup)

    def on_config_loaded(self, event: ConfigLoadedEvent) -> None:
        self._global_config = event.config
        self._project_dir = self._global_config.project_dir
        self._default_scenarios_dir = Path(self._global_config.default_scenarios_dir).resolve()

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        event.arg_parser.add_argument("file_or_dir", nargs="*",
                                      default=[self._default_scenarios_dir],
                                      help="Select scenarios in a given file or directory")
        event.arg_parser.add_argument("-i", "--ignore", nargs="+",
                                      default=[],
                                      help="Skip scenarios in a given file or directory")
        event.arg_parser.add_argument("--subject", help="Select scenarios with a given subject")

        help_message = (
            "Enable the experimental selective discoverer feature to optimize startup speed "
            "by loading scenarios only from specified files. "
            "This is particularly beneficial for very large test suites "
            "where Python's import mechanism can be slow, "
            "thus reducing the initial load time and improving overall test execution efficiency."
        )
        event.arg_parser.add_argument("--exp-selective-discoverer", action="store_true",
                                      default=self._exp_selective_discoverer,
                                      help=help_message)

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        self._subject = event.args.subject

        for file_or_dir in event.args.file_or_dir:
            composite_path = self._get_composite_path(file_or_dir)
            path = composite_path.file_path
            assert os.path.isdir(path) or os.path.isfile(path), f"{path!r} does not exist"
            self._selected.append(composite_path)

        for file_or_dir in event.args.ignore:
            composite_path = self._get_composite_path(file_or_dir)
            path = composite_path.file_path
            assert os.path.isdir(path) or os.path.isfile(path), f"{path!r} does not exist"
            self._deselected.append(composite_path)

        self._exp_selective_discoverer = event.args.exp_selective_discoverer
        if not self._exp_selective_discoverer:
            return
        if len(self._deselected) == 0 and (self._subject is None):
            assert self._global_config is not None  # for type checking
            self._global_config.Registry.ScenarioDiscoverer.register(lambda: ScenarioDiscoverer(
                finder=self._global_config.Registry.ScenarioFinder(),
                loader=self._global_config.Registry.ScenarioLoader(),
                orderer=self._global_config.Registry.ScenarioOrderer(),
                selected_paths=self.__get_selected_paths(),
            ), self)

    def __get_selected_paths(self) -> Set[Path]:
        selected_paths = set()
        for path in self._selected:
            file_path = Path(path.file_path)
            if file_path != self._default_scenarios_dir:
                selected_paths.add(file_path)
        return selected_paths

    def _get_composite_path(self, file_or_dir: str) -> _CompositePath:
        head, tail = os.path.split(file_or_dir)
        file_name, *other = tail.split("::")
        cls_name, *other = "".join(other).split("#")
        tmpl_idx = "".join(other)
        return _CompositePath(
            file_path=self._normalize_path(os.path.join(head, file_name)),
            cls_name=cls_name if len(cls_name) > 0 else None,
            tmpl_idx=int(tmpl_idx) if tmpl_idx.isnumeric() else None,
        )

    def _normalize_path(self, file_or_dir: str) -> str:
        path = os.path.normpath(file_or_dir)
        if os.path.isabs(path):
            return path

        # Backward compatibility (to be removed in v2):
        # Only prepend "scenarios/" if:
        # 1) The default_scenarios_dir is exactly <project_dir>/scenarios
        # 2) The original path does not exist, but "scenarios/<path>" does
        if self._default_scenarios_dir == self._project_dir / "scenarios":  # type: ignore
            updated_path = os.path.join("scenarios/", path)
            if not os.path.exists(path) and os.path.exists(updated_path):
                return os.path.abspath(updated_path)

        return os.path.abspath(path)

    def _is_scenario_special(self, scenario: VirtualScenario) -> bool:
        return scenario.get_meta("only", default=False, plugin=self,
                                 fallback_key="__vedro__only__")

    def _is_scenario_skipped(self, scenario: VirtualScenario) -> bool:
        return scenario.get_meta("skipped", default=False, plugin=self,
                                 fallback_key="__vedro__skipped__")

    def _get_skip_reason(self, scenario: VirtualScenario) -> Union[str, None]:
        return scenario.get_meta("skip_reason", default=None, plugin=self,
                                 fallback_key="__vedro__skip_reason__")

    def _is_match_scenario(self, path: _CompositePath, scenario: VirtualScenario) -> bool:
        if os.path.commonpath([path.file_path, scenario.path]) != path.file_path:
            return False

        if (path.cls_name is not None) and (path.cls_name != scenario.name):
            return False

        if (path.tmpl_idx is not None) and (path.tmpl_idx != scenario.template_index):
            return False

        return True

    def _is_scenario_selected(self, scenario: VirtualScenario) -> bool:
        for path in self._selected:
            if self._is_match_scenario(path, scenario):
                return True
        return False

    def _is_scenario_deselected(self, scenario: VirtualScenario) -> bool:
        for path in self._deselected:
            if self._is_match_scenario(path, scenario):
                return True
        return False

    def _is_scenario_ignored(self, scenario: VirtualScenario) -> bool:
        if self._subject and scenario.subject != self._subject:
            return True

        if not self._is_scenario_selected(scenario):
            return True

        if self._is_scenario_deselected(scenario):
            return True

        return False

    async def on_startup(self, event: StartupEvent) -> None:
        special_scenarios = set()

        scheduler = event.scheduler
        async for scenario in scheduler:
            if self._is_scenario_ignored(scenario):
                scheduler.ignore(scenario)
            else:
                if self._is_scenario_skipped(scenario):
                    scenario.skip(reason=self._get_skip_reason(scenario))
                if self._is_scenario_special(scenario):
                    if self._forbid_only:
                        raise ValueError(f"Scenario '{scenario.unique_id}' has @vedro.only, but "
                                         "'forbid_only' option is enabled")
                    special_scenarios.add(scenario.unique_id)

        if len(special_scenarios) > 0:
            async for scenario in scheduler:
                if scenario.unique_id not in special_scenarios:
                    scheduler.ignore(scenario)


class Skipper(PluginConfig):
    plugin = SkipperPlugin
    description = ("Allows selective scenario skipping and selection "
                   "based on file/directory or subject")

    # Forbid execution of scenarios with '@vedro.only' decorator
    forbid_only: bool = False

    # Enable the experimental selective discoverer feature
    # to optimize startup speed by loading scenarios only from specified files
    exp_selective_discoverer: bool = False
