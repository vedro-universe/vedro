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

from ._scheduler import RepeaterScenarioScheduler

__all__ = ("Repeater", "RepeaterPlugin",)


class RepeaterPlugin(Plugin):
    def __init__(self, config: Type["Repeater"]) -> None:
        super().__init__(config)
        self._repeats: int = 0
        self._scheduler: Union[ScenarioScheduler, None] = None
        self._repeat_scenario_id: Union[str, None] = None

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ArgParseEvent, self.on_arg_parse) \
                  .listen(ArgParsedEvent, self.on_arg_parsed) \
                  .listen(StartupEvent, self.on_startup) \
                  .listen(ScenarioPassedEvent, self.on_scenario_end) \
                  .listen(ScenarioFailedEvent, self.on_scenario_end) \
                  .listen(CleanupEvent, self.on_cleanup)

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        group = event.arg_parser.add_argument_group("Repeater")
        group.add_argument("--repeats", type=int, default=0,
                           help="Number of times to repeat scenarios (default: 0)")

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        self._repeats = event.args.repeats

    def on_startup(self, event: StartupEvent) -> None:
        self._scheduler = event.scheduler  # type: ignore

    def on_scenario_end(self, event:  Union[ScenarioPassedEvent, ScenarioFailedEvent]) -> None:
        if (self._repeats == 0) or not isinstance(self._scheduler, RepeaterScenarioScheduler):
            return

        if self._repeat_scenario_id == event.scenario_result.scenario.unique_id:
            return

        self._repeat_scenario_id = event.scenario_result.scenario.unique_id
        for _ in range(self._repeats):
            self._scheduler.schedule(event.scenario_result.scenario)

    def on_cleanup(self, event: CleanupEvent) -> None:
        if self._repeats != 0:
            event.report.add_summary(f"repeated x{self._repeats}")


class Repeater(PluginConfig):
    plugin = RepeaterPlugin
