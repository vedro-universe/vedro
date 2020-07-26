import os
from typing import Any, List, Union

from ..._core import Dispatcher
from ..._core._virtual_scenario import VirtualScenario
from ..._events import ArgParsedEvent, ArgParseEvent, StartupEvent
from ..plugin import Plugin


class Skipper(Plugin):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._subject: Union[str, None] = None
        self._specified: List[str] = []
        self._ignored: List[str] = []

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ArgParseEvent, self.on_arg_parse) \
                  .listen(ArgParsedEvent, self.on_arg_parsed) \
                  .listen(StartupEvent, self.on_startup)

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        event.arg_parser.add_argument("file_or_dir", nargs='*', default=["."])
        event.arg_parser.add_argument("-i", "--ignore", nargs='+', default=[])
        event.arg_parser.add_argument("-s", "--subject")

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        self._subject = event.args.subject

        for file_or_dir in event.args.file_or_dir:
            path = self._normalize_path(file_or_dir)
            assert os.path.isdir(path) or os.path.isfile(path), f"{path!r} does not exist"
            self._specified.append(path)

        for file_or_dir in event.args.ignore:
            path = self._normalize_path(file_or_dir)
            assert os.path.isdir(path) or os.path.isfile(path), f"{path!r} does not exist"
            self._ignored.append(path)

    def _normalize_path(self, file_or_dir: str) -> str:
        path = os.path.normpath(file_or_dir)
        if os.path.isabs(path):
            return path
        if os.path.commonpath(["scenarios", path]) != "scenarios":
            path = os.path.join("scenarios", path)
        return os.path.abspath(path)

    def _is_scenario_skipped(self, scenario: VirtualScenario) -> bool:
        if getattr(scenario.scenario, "__vedro__skipped__", False):
            return True
        template = getattr(scenario.scenario, "__vedro__template__", None)
        if getattr(template, "__vedro__skipped__", False):
            return True
        if self._subject and scenario.subject != self._subject:
            return True
        if not self._is_scenario_specified(scenario):
            return True
        if self._is_scenario_ignored(scenario):
            return True
        return False

    def _is_scenario_special(self, scenario: VirtualScenario) -> bool:
        if getattr(scenario.scenario, "__vedro__only__", False):
            return True
        template = getattr(scenario.scenario, "__vedro__template__", None)
        if getattr(template, "__vedro__only__", False):
            return True
        return False

    def _is_scenario_specified(self, scenario: VirtualScenario) -> bool:
        for path in self._specified:
            if os.path.commonpath([path, scenario.path]) == path:
                return True
        return False

    def _is_scenario_ignored(self, scenario: VirtualScenario) -> bool:
        for path in self._ignored:
            if os.path.commonpath([path, scenario.path]) == path:
                return True
        return False

    def on_startup(self, event: StartupEvent) -> None:
        special_scenarios = set()
        for scenario in event.scenarios:
            if self._is_scenario_skipped(scenario):
                scenario.mark_skipped()
            elif self._is_scenario_special(scenario):
                special_scenarios.add(scenario)

        if len(special_scenarios) > 0:
            for scenario in event.scenarios:
                if scenario not in special_scenarios:
                    scenario.mark_skipped()
