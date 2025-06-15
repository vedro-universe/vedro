from typing import Set, Type, final

from niltype import Nil

from vedro.core import Dispatcher, Plugin, PluginConfig
from vedro.core.exp.local_storage import LocalStorageFactory, create_local_storage
from vedro.events import (
    ArgParsedEvent,
    ArgParseEvent,
    CleanupEvent,
    ConfigLoadedEvent,
    ScenarioReportedEvent,
    StartupEvent,
)

__all__ = ("LastFailed", "LastFailedPlugin",)


@final
class LastFailedPlugin(Plugin):
    """
    Plugin that allows rerunning only the previously failed scenarios.

    The `LastFailedPlugin` listens to events during test execution, tracks failed scenarios,
    and stores their IDs in local storage. On subsequent test runs, it provides an option
    to rerun only the scenarios that failed in the previous execution.
    """

    def __init__(self, config: Type["LastFailed"], *,
                 local_storage_factory: LocalStorageFactory = create_local_storage) -> None:
        """
        Initialize the LastFailedPlugin with the provided configuration.

        :param config: The LastFailed configuration class.
        :param local_storage_factory: Factory function to create local storage.
            Defaults to `create_local_storage`.
        """
        super().__init__(config)
        self._local_storage_factory = local_storage_factory
        self._last_failed = False
        self._failed_scenarios: Set[str] = set()

    def subscribe(self, dispatcher: Dispatcher) -> None:
        """
        Subscribe to Vedro events to track scenario execution and handle last failed logic.

        :param dispatcher: The event dispatcher to register listeners on.
        """
        dispatcher.listen(ConfigLoadedEvent, self.on_config_loaded) \
                  .listen(ArgParseEvent, self.on_arg_parse) \
                  .listen(ArgParsedEvent, self.on_arg_parsed) \
                  .listen(StartupEvent, self.on_startup) \
                  .listen(ScenarioReportedEvent, self.on_scenario_reported) \
                  .listen(CleanupEvent, self.on_cleanup)

    def on_config_loaded(self, event: ConfigLoadedEvent) -> None:
        """
        Handle the event when the configuration is loaded.

        Initializes the local storage based on the project directory.

        :param event: The ConfigLoadedEvent instance containing the loaded configuration.
        """
        self._local_storage = self._local_storage_factory(self, event.config.project_dir)

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        """
        Add the `--last-failed` argument for rerunning only the failed scenarios.

        :param event: The ArgParseEvent instance used for adding arguments.
        """
        group = event.arg_parser.add_argument_group("Last Failed")
        group.add_argument("--last-failed", action="store_true", default=self._last_failed,
                           help="Run only last failed scenarios")

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        """
        Handle the event after arguments have been parsed.

        Sets the flag to indicate whether to run only the last failed scenarios.

        :param event: The ArgParsedEvent instance containing parsed arguments.
        """
        self._last_failed = event.args.last_failed

    async def on_startup(self, event: StartupEvent) -> None:
        """
        Handle the startup event by filtering scenarios to run only the failed ones.

        If the `--last-failed` flag is set, retrieves the previously failed scenarios
        from local storage and instructs the scheduler to ignore scenarios that did not fail.

        :param event: The StartupEvent instance containing the scheduler.
        """
        if not self._last_failed:
            return

        last_failed = await self._local_storage.get("last_failed")
        failed_scenarios = set(last_failed) if (last_failed is not Nil) else set()

        async for scenario in event.scheduler:
            if scenario.unique_id not in failed_scenarios:
                event.scheduler.ignore(scenario)

    def on_scenario_reported(self, event: ScenarioReportedEvent) -> None:
        """
        Handle the event when a scenario has been reported, tracking failed scenarios.

        If the scenario has failed, its unique ID is added to the set of failed scenarios.

        :param event: The ScenarioReportedEvent instance.
        """
        if event.aggregated_result.is_failed():
            unique_id = event.aggregated_result.scenario.unique_id
            self._failed_scenarios.add(unique_id)

    async def on_cleanup(self, event: CleanupEvent) -> None:
        """
        Handle the cleanup event, saving the failed scenarios to local storage.

        After all scenarios have been executed, the failed scenarios are stored in the
        local storage, and the data is flushed to ensure persistence.

        :param event: The CleanupEvent instance.
        """
        await self._local_storage.put("last_failed", list(self._failed_scenarios))
        await self._local_storage.flush()


class LastFailed(PluginConfig):
    """
    Configuration class for the LastFailedPlugin.

    Provides the option to run only the scenarios that failed during the last test execution.
    """

    plugin = LastFailedPlugin
    description = "Runs only the previously failed scenarios"
