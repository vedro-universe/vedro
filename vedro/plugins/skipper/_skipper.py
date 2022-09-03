import os
from typing import List, Optional, Type, Union

from vedro.core import Dispatcher, Plugin, PluginConfig, VirtualScenario
from vedro.events import ArgParsedEvent, ArgParseEvent, StartupEvent

__all__ = ("Skipper", "SkipperPlugin",)


class _CompositePath:
    def __init__(self, file_path: str, cls_name: Optional[str], tmpl_idx: Optional[int]) -> None:
        self.file_path = file_path
        self.cls_name = cls_name
        self.tmpl_idx = tmpl_idx


class SkipperPlugin(Plugin):
    def __init__(self, config: Type["Skipper"]) -> None:
        super().__init__(config)
        self._subject: Union[str, None] = None
        self._selected: List[_CompositePath] = []
        self._deselected: List[_CompositePath] = []

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ArgParseEvent, self.on_arg_parse) \
                  .listen(ArgParsedEvent, self.on_arg_parsed) \
                  .listen(StartupEvent, self.on_startup)

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        event.arg_parser.add_argument("file_or_dir", nargs="*", default=["."],
                                      help="Select scenarios in a given file or directory")
        event.arg_parser.add_argument("-i", "--ignore", nargs="+", default=[],
                                      help="Skip scenarios in a given file or directory")
        event.arg_parser.add_argument("--subject", help="Select scenarios with a given subject")

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
        if os.path.commonpath(["scenarios", path]) != "scenarios":
            path = os.path.join("scenarios", path)
        return os.path.abspath(path)

    def _is_scenario_skipped(self, scenario: VirtualScenario) -> bool:
        template = getattr(scenario._orig_scenario, "__vedro__template__", None)
        return getattr(template or scenario._orig_scenario, "__vedro__skipped__", False)

    def _is_scenario_special(self, scenario: VirtualScenario) -> bool:
        template = getattr(scenario._orig_scenario, "__vedro__template__", None)
        return getattr(template or scenario._orig_scenario, "__vedro__only__", False)

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
                    scenario.skip()
                if self._is_scenario_special(scenario):
                    special_scenarios.add(scenario.unique_id)

        if len(special_scenarios) > 0:
            async for scenario in scheduler:
                if scenario.unique_id not in special_scenarios:
                    scheduler.ignore(scenario)


class Skipper(PluginConfig):
    plugin = SkipperPlugin
