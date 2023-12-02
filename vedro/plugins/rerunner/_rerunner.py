import asyncio
from typing import Any, Callable, Coroutine, Type, Union

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

from ._scheduler import RerunnerScenarioScheduler

__all__ = ("Rerunner", "RerunnerPlugin",)

SleepType = Callable[[float], Coroutine[Any, Any, None]]


class RerunnerPlugin(Plugin):
    def __init__(self, config: Type["Rerunner"], *, sleep: SleepType = asyncio.sleep) -> None:
        super().__init__(config)
        self._scheduler_factory = config.scheduler_factory
        self._sleep = sleep
        self._reruns: int = 0
        self._reruns_delay: float = 0.0
        self._global_config: Union[ConfigType, None] = None
        self._scheduler: Union[ScenarioScheduler, None] = None
        self._rerun_scenario_id: Union[str, None] = None
        self._reran: int = 0
        self._times: int = 0

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
        group = event.arg_parser.add_argument_group("Rerunner")
        group.add_argument("--reruns", type=int, default=self._reruns,
                           help="Number of times to rerun failed scenarios (default: 0)")
        group.add_argument("--reruns-delay", type=float, default=self._reruns_delay,
                           help="Delay in seconds between reruns (default: 0.0s)")

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        self._reruns = event.args.reruns
        self._reruns_delay = event.args.reruns_delay

        if self._reruns < 0:
            raise ValueError("--reruns must be >= 0")

        if self._reruns_delay < 0.0:
            raise ValueError("--reruns-delay must be >= 0.0")

        if self._reruns_delay > 0.0 and self._reruns < 1:
            raise ValueError("--reruns-delay must be used with --reruns > 0")

        if self._reruns == 0:
            return

        assert self._global_config is not None  # for type checking
        self._global_config.Registry.ScenarioScheduler.register(self._scheduler_factory, self)

    def on_startup(self, event: StartupEvent) -> None:
        self._scheduler = event.scheduler

    async def on_scenario_end(self,
                              event: Union[ScenarioPassedEvent, ScenarioFailedEvent]) -> None:
        if self._reruns == 0:
            return

        assert isinstance(self._scheduler, RerunnerScenarioScheduler)  # for type checking

        if self._rerun_scenario_id == event.scenario_result.scenario.unique_id:
            return

        self._rerun_scenario_id = event.scenario_result.scenario.unique_id
        if event.scenario_result.is_failed():
            self._reran += 1
            for _ in range(self._reruns):
                if self._reruns_delay > 0.0:
                    await self._sleep(self._reruns_delay)
                self._scheduler.schedule(event.scenario_result.scenario)
                self._times += 1

    def on_cleanup(self, event: CleanupEvent) -> None:
        if self._reruns != 0:
            ss = "" if self._reran == 1 else "s"
            ts = "" if self._times == 1 else "s"
            message = f"rerun {self._reran} scenario{ss}, {self._times} time{ts}"
            if self._reruns_delay:
                message += f", with delay {self._reruns_delay!r}s"
            event.report.add_summary(message)


class Rerunner(PluginConfig):
    plugin = RerunnerPlugin
    description = "Reruns failed scenarios a specified number of times"

    # Scheduler that will be used to create aggregated result for rerun scenarios
    scheduler_factory: Type[ScenarioScheduler] = RerunnerScenarioScheduler
