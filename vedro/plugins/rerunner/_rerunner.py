import asyncio
from typing import Any, Callable, Coroutine, Type, Union, final

from vedro.core import ConfigType, Dispatcher, Plugin, PluginConfig, ScenarioScheduler
from vedro.events import (
    ArgParsedEvent,
    ArgParseEvent,
    CleanupEvent,
    ConfigLoadedEvent,
    ScenarioFailedEvent,
    ScenarioPassedEvent,
    ScenarioRunEvent,
    ScenarioSkippedEvent,
    StartupEvent,
)

from ._scheduler import RerunnerScenarioScheduler

__all__ = ("Rerunner", "RerunnerPlugin",)

SleepType = Callable[[float], Coroutine[Any, Any, None]]


@final
class RerunnerPlugin(Plugin):
    """
    Plugin to rerun failed scenarios a specified number of times.

    The RerunnerPlugin allows failed scenarios to be rerun multiple times as configured.
    It supports delays between reruns and aggregates the results to determine the final
    outcome based on the majority of rerun attempts.
    """

    def __init__(self, config: Type["Rerunner"], *, sleep: SleepType = asyncio.sleep) -> None:
        """
        Initialize the RerunnerPlugin with the provided configuration.

        This constructor initializes the RerunnerPlugin with the settings for
        scenario reruns, including the number of reruns, delay between reruns,
        and a custom sleep function for introducing delays.

        :param config: The Rerunner configuration class.
        :param sleep: Coroutine for introducing delays (default: `asyncio.sleep`).
        """
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
        """
        Subscribe to the necessary Vedro events for managing scenario reruns.

        This method registers event listeners for configuration loading, argument
        parsing, scenario execution, and cleanup, enabling the RerunnerPlugin to
        manage the rerunning of failed scenarios.

        :param dispatcher: The event dispatcher to register listeners on.
        """
        dispatcher.listen(ConfigLoadedEvent, self.on_config_loaded) \
                  .listen(ArgParseEvent, self.on_arg_parse) \
                  .listen(ArgParsedEvent, self.on_arg_parsed) \
                  .listen(StartupEvent, self.on_startup) \
                  .listen(ScenarioRunEvent, self.on_scenario_execute) \
                  .listen(ScenarioSkippedEvent, self.on_scenario_execute) \
                  .listen(ScenarioPassedEvent, self.on_scenario_end) \
                  .listen(ScenarioFailedEvent, self.on_scenario_end) \
                  .listen(CleanupEvent, self.on_cleanup)

    def on_config_loaded(self, event: ConfigLoadedEvent) -> None:
        """
        Handle the event when the configuration is loaded.

        This method stores the global configuration, which is necessary for
        registering the custom scenario scheduler for rerunning failed scenarios.

        :param event: The ConfigLoadedEvent containing the loaded configuration.
        """
        self._global_config = event.config

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        """
        Handle the event when arguments are being parsed, adding rerun-related arguments.

        This method adds command-line options for controlling the number of scenario
        reruns, and the delay between reruns, allowing users to configure the plugin.

        :param event: The ArgParseEvent containing the argument parser.
        """
        group = event.arg_parser.add_argument_group("Rerunner")
        help_message = ("Number of times to rerun failed scenarios (default: 0). "
                        "The resulting scenario status is based on the majority of rerun results.")
        group.add_argument("--reruns", type=int, default=self._reruns, help=help_message)
        group.add_argument("--reruns-delay", type=float, default=self._reruns_delay,
                           help="Delay in seconds between reruns (default: 0.0s)")

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        """
        Handle the event after arguments have been parsed, applying rerun settings.

        This method processes the parsed arguments and applies them to configure the
        number of reruns and any delays between reruns. It raises errors if invalid
        combinations of arguments are provided.

        :param event: The ArgParsedEvent containing the parsed arguments.
        :raises ValueError: If invalid values are provided for reruns or delays.
        """
        self._reruns = event.args.reruns
        self._reruns_delay = event.args.reruns_delay

        if self._reruns < 0:
            raise ValueError("--reruns must be >= 0")

        if self._reruns_delay < 0.0:
            raise ValueError("--reruns-delay must be >= 0.0")

        if (self._reruns_delay > 0.0) and (self._reruns < 1):
            raise ValueError("--reruns-delay must be used with --reruns > 0")

        if self._is_rerunning_enabled():
            assert self._global_config is not None  # for type checking
            self._global_config.Registry.ScenarioScheduler.register(self._scheduler_factory, self)

    def on_startup(self, event: StartupEvent) -> None:
        """
        Handle the startup event, storing the scenario scheduler.

        This method captures the scenario scheduler from the startup event,
        enabling it to manage scheduling of rerun scenarios.

        :param event: The StartupEvent instance signaling system startup.
        """
        self._scheduler = event.scheduler

    async def on_scenario_execute(self,
                                  event: Union[ScenarioRunEvent, ScenarioSkippedEvent]) -> None:
        """
        Handle the event when a scenario is executed or skipped, managing reruns.

        This method ensures that if a scenario is rerun, a delay is applied
        between reruns if configured.

        :param event: The ScenarioRunEvent or ScenarioSkippedEvent instance.
        """
        if not self._is_rerunning_enabled():
            return

        scenario = event.scenario_result.scenario
        if (self._rerun_scenario_id == scenario.unique_id) and (self._reruns_delay > 0.0):
            await self._sleep(self._reruns_delay)

    async def on_scenario_end(self,
                              event: Union[ScenarioPassedEvent, ScenarioFailedEvent]) -> None:
        """
        Handle the event when a scenario ends, scheduling additional reruns if necessary.

        This method tracks scenario results and schedules additional reruns if the
        scenario has not been rerun the configured number of times.

        :param event: The ScenarioPassedEvent or ScenarioFailedEvent instance.
        """
        if not self._is_rerunning_enabled():
            return
        assert isinstance(self._scheduler, ScenarioScheduler)  # for type checking

        scenario = event.scenario_result.scenario
        if scenario.unique_id != self._rerun_scenario_id:
            self._rerun_scenario_id = scenario.unique_id

            if event.scenario_result.is_failed():
                self._reran += 1
                for _ in range(self._reruns):
                    self._scheduler.schedule(scenario)
                    self._times += 1

    def on_cleanup(self, event: CleanupEvent) -> None:
        """
        Handle the cleanup event, adding a summary of the rerun process.

        This method generates a summary message detailing how many scenarios were rerun,
        how many reruns occurred in total, and if any delays were applied.

        :param event: The CleanupEvent signaling the end of execution.
        """
        if not self._is_rerunning_enabled():
            return
        message = self._get_summary_message()
        event.report.add_summary(message)

    def _is_rerunning_enabled(self) -> bool:
        """
        Check if scenario rerunning is enabled.

        :return: True if reruns are enabled, False otherwise.
        """
        return self._reruns > 0

    def _get_summary_message(self) -> str:
        """
        Generate a summary message for the rerun process.

        This method returns a string summarizing the rerun process, including
        the number of reruns and any delays applied.

        :return: A string summarizing the rerun process.
        """
        ss = "" if self._reran == 1 else "s"
        ts = "" if self._times == 1 else "s"
        message = f"rerun {self._reran} scenario{ss}, {self._times} time{ts}"
        if self._reruns_delay:
            message += f", with delay {self._reruns_delay!r}s"
        return message


class Rerunner(PluginConfig):
    """
    Configuration class for the RerunnerPlugin.

    This class defines the configuration options for the RerunnerPlugin, including
    the scheduler factory used for managing rerun scenario executions.
    """

    plugin = RerunnerPlugin
    description = "Reruns failed scenarios a specified number of times"

    # Scheduler that will be used to create aggregated result for rerun scenarios
    scheduler_factory: Type[ScenarioScheduler] = RerunnerScenarioScheduler
