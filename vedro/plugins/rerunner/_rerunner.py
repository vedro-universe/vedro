from typing import Type, Union

from vedro.core import Dispatcher
from vedro.core import MonotonicScenarioScheduler as ScenarioScheduler
from vedro.core import Plugin, PluginConfig
from vedro.events import (
    ArgParsedEvent,
    ArgParseEvent,
    CleanupEvent,
    ScenarioFailedEvent,
    ScenarioPassedEvent,
    StartupEvent,
)

from ._scheduler import RerunnerScenarioScheduler

__all__ = ("Rerunner", "RerunnerPlugin",)


class RerunnerPlugin(Plugin):
    def __init__(self, config: Type["Rerunner"]) -> None:
        super().__init__(config)
        self._reruns: int = 0
        self._scheduler: Union[ScenarioScheduler, None] = None
        self._rerun_scenario_id: Union[str, None] = None
        self._reran: int = 0
        self._times: int = 0

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ArgParseEvent, self.on_arg_parse) \
                  .listen(ArgParsedEvent, self.on_arg_parsed) \
                  .listen(StartupEvent, self.on_startup) \
                  .listen(ScenarioPassedEvent, self.on_scenario_end) \
                  .listen(ScenarioFailedEvent, self.on_scenario_end) \
                  .listen(CleanupEvent, self.on_cleanup)

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        group = event.arg_parser.add_argument_group("Rerunner")
        group.add_argument("--reruns", type=int, default=0,
                           help="Number of times to rerun failed scenarios (default: 0)")

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        self._reruns = event.args.reruns

    def on_startup(self, event: StartupEvent) -> None:
        self._scheduler = event.scheduler

    def on_scenario_end(self, event:  Union[ScenarioPassedEvent, ScenarioFailedEvent]) -> None:
        if (self._reruns == 0) or not isinstance(self._scheduler, RerunnerScenarioScheduler):
            return

        if self._rerun_scenario_id == event.scenario_result.scenario.unique_id:
            return

        self._rerun_scenario_id = event.scenario_result.scenario.unique_id
        if event.scenario_result.is_failed():
            self._reran += 1
            for _ in range(self._reruns):
                self._scheduler.schedule(event.scenario_result.scenario)
                self._times += 1

    def on_cleanup(self, event: CleanupEvent) -> None:
        if self._reruns != 0:
            ss = "" if self._reran == 1 else "s"
            ts = "" if self._times == 1 else "s"
            event.report.add_summary(f"rerun {self._reran} scenario{ss}, {self._times} time{ts}")


class Rerunner(PluginConfig):
    plugin = RerunnerPlugin
