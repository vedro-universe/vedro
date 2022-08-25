from typing import Type, Union

from vedro.core import ConfigType, Dispatcher, Plugin, PluginConfig, ScenarioScheduler
from vedro.events import (
    ArgParsedEvent,
    ArgParseEvent,
    CleanupEvent,
    ConfigLoadedEvent,
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
        self._global_config: Union[ConfigType, None] = None
        self._scheduler: Union[ScenarioScheduler, None] = None
        self._repeat_scenario_id: Union[str, None] = None

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ConfigLoadedEvent, self.on_config_loaded) \
                  .listen(ArgParseEvent, self.on_arg_parse) \
                  .listen(ArgParsedEvent, self.on_arg_parsed) \
                  .listen(StartupEvent, self.on_startup) \
                  .listen(ScenarioPassedEvent, self.on_scenario_end) \
                  .listen(ScenarioFailedEvent, self.on_scenario_end) \
                  .listen(CleanupEvent, self.on_cleanup)

    def on_config_loaded(self, event: ConfigLoadedEvent) -> None:
        self._global_config = event.config

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        group = event.arg_parser.add_argument_group("Repeater")
        group.add_argument("-N", "--repeats", type=int, default=1,
                           help="Number of times to repeat scenarios (default: 1)")

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        self._repeats = event.args.repeats
        assert self._repeats >= 1

        if self._repeats <= 1:
            return

        assert self._global_config is not None
        self._global_config.Registry.ScenarioScheduler.register(RepeaterScenarioScheduler, self)

    def on_startup(self, event: StartupEvent) -> None:
        self._scheduler = event.scheduler

    def on_scenario_end(self, event:  Union[ScenarioPassedEvent, ScenarioFailedEvent]) -> None:
        if self._repeats <= 1:
            return

        assert isinstance(self._scheduler, RepeaterScenarioScheduler)

        if self._repeat_scenario_id == event.scenario_result.scenario.unique_id:
            return

        self._repeat_scenario_id = event.scenario_result.scenario.unique_id
        for _ in range(self._repeats - 1):
            self._scheduler.schedule(event.scenario_result.scenario)

    def on_cleanup(self, event: CleanupEvent) -> None:
        if self._repeats > 1:
            event.report.add_summary(f"repeated x{self._repeats}")


class Repeater(PluginConfig):
    plugin = RepeaterPlugin
