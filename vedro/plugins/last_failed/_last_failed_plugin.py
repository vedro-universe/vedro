from typing import Set, Type

from niltype import Nil

from vedro.core import Dispatcher, Plugin, PluginConfig
from vedro.core.exp.local_storage import LocalStorageFactory, create_local_storage
from vedro.events import (
    ArgParsedEvent,
    ArgParseEvent,
    CleanupEvent,
    ScenarioReportedEvent,
    StartupEvent,
)

__all__ = ("LastFailed", "LastFailedPlugin",)


class LastFailedPlugin(Plugin):
    def __init__(self, config: Type["LastFailed"], *,
                 local_storage_factory: LocalStorageFactory = create_local_storage) -> None:
        super().__init__(config)
        self._local_storage = local_storage_factory(self)
        self._last_failed = False
        self._failed_scenarios: Set[str] = set()

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ArgParseEvent, self.on_arg_parse) \
            .listen(ArgParsedEvent, self.on_arg_parsed) \
            .listen(StartupEvent, self.on_startup) \
            .listen(ScenarioReportedEvent, self.on_scenario_reported) \
            .listen(CleanupEvent, self.on_cleanup)

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        group = event.arg_parser.add_argument_group("Last Failed")
        group.add_argument("--last-failed", action="store_true", default=self._last_failed,
                           help="Run only last failed scenarios")

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        self._last_failed = event.args.last_failed

    async def on_startup(self, event: StartupEvent) -> None:
        if not self._last_failed:
            return

        last_failed = await self._local_storage.get("last_failed")
        failed_scenarios = set(last_failed) if (last_failed is not Nil) else set()

        async for scenario in event.scheduler:
            if scenario.unique_id not in failed_scenarios:
                event.scheduler.ignore(scenario)

    def on_scenario_reported(self, event: ScenarioReportedEvent) -> None:
        if event.aggregated_result.is_failed():
            unique_id = event.aggregated_result.scenario.unique_id
            self._failed_scenarios.add(unique_id)

    async def on_cleanup(self, event: CleanupEvent) -> None:
        await self._local_storage.put("last_failed", list(self._failed_scenarios))
        await self._local_storage.flush()


class LastFailed(PluginConfig):
    plugin = LastFailedPlugin
    description = "Runs only the previously failed scenarios"
