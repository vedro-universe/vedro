from typing import Type, Union

from vedro.core import Dispatcher, Plugin, PluginConfig
from vedro.core import QueuedScenarioScheduler as ScenarioScheduler
from vedro.events import (
    ArgParsedEvent,
    ArgParseEvent,
    ScenarioFailedEvent,
    ScenarioPassedEvent,
    StartupEvent,
)

__all__ = ("Rerunner", "RerunnerPlugin",)


class RerunnerPlugin(Plugin):
    def __init__(self, config: Type["Rerunner"]) -> None:
        super().__init__(config)
        self._reruns: int = 0
        self._scheduler: Union[ScenarioScheduler, None] = None
        self._rerun_scenario_id: Union[str, None] = None

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ArgParseEvent, self.on_arg_parse) \
                  .listen(ArgParsedEvent, self.on_arg_parsed) \
                  .listen(StartupEvent, self.on_startup) \
                  .listen(ScenarioPassedEvent, self.on_scenario_end) \
                  .listen(ScenarioFailedEvent, self.on_scenario_end)

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        group = event.arg_parser.add_argument_group("Rerunner")
        group.add_argument("--reruns", type=int, default=0,
                           help="Number of times to rerun failed scenarios (default: 0)")

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        self._reruns = event.args.reruns

    def on_startup(self, event: StartupEvent) -> None:
        if isinstance(event.scheduler, ScenarioScheduler):
            self._scheduler = event.scheduler

    def on_scenario_end(self, event:  Union[ScenarioPassedEvent, ScenarioFailedEvent]) -> None:
        if (self._reruns == 0) or (self._scheduler is None):
            return

        if self._rerun_scenario_id == event.scenario_result.scenario.unique_id:
            return

        self._rerun_scenario_id = event.scenario_result.scenario.unique_id
        if event.scenario_result.is_failed():
            for _ in range(self._reruns):
                self._scheduler.add(event.scenario_result.scenario)


class Rerunner(PluginConfig):
    plugin = RerunnerPlugin
