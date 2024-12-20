import asyncio
from typing import Any, Callable, Coroutine, Type, Union, final

from vedro.core import ConfigType, Dispatcher, Plugin, PluginConfig, ScenarioScheduler
from vedro.core.scenario_runner import Interrupted
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

from ._scheduler import RepeaterScenarioScheduler

__all__ = ("Repeater", "RepeaterPlugin", "RepeaterExecutionInterrupted",)


class RepeaterExecutionInterrupted(Interrupted):
    """
    Exception raised when the execution of scenario repetition is interrupted.

    This exception is used within the RepeaterPlugin to signal an early termination
    of the scenario repetition process. It is typically raised when the fail-fast
    condition is met, i.e., if a scenario fails and the --fail-fast-on-repeat option
    is enabled, indicating that further repetitions of the scenario should be stopped.
    """
    pass


SleepType = Callable[[float], Coroutine[Any, Any, None]]


@final
class RepeaterPlugin(Plugin):
    """
    Plugin to repeat scenario execution a specified number of times.

    The RepeaterPlugin allows scenarios to be executed multiple times as configured.
    It supports delays between repetitions and can stop execution early if the
    fail-fast-on-repeat option is enabled.
    """

    def __init__(self, config: Type["Repeater"], *, sleep: SleepType = asyncio.sleep) -> None:
        """
        Initialize the RepeaterPlugin with the provided configuration.

        This constructor initializes the RepeaterPlugin with the settings for
        scenario repetition, including the number of repetitions, delay between
        repetitions, and whether fail-fast behavior is enabled.

        :param config: The Repeater configuration class.
        :param sleep: Coroutine for introducing delays (default: `asyncio.sleep`).
        """
        super().__init__(config)
        self._scheduler_factory = config.scheduler_factory
        self._sleep = sleep
        self._repeats: int = 1
        self._repeats_delay: float = 0.0
        self._fail_fast: bool = False
        self._global_config: Union[ConfigType, None] = None
        self._scheduler: Union[ScenarioScheduler, None] = None
        self._repeat_scenario_id: Union[str, None] = None
        self._failed_count: int = 0

    def subscribe(self, dispatcher: Dispatcher) -> None:
        """
        Subscribe to the necessary Vedro events for managing scenario repetitions.

        This method registers event listeners for configuration loading, argument
        parsing, scenario execution, and cleanup, enabling the RepeaterPlugin to
        manage repeated scenario executions.

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
        registering the custom scenario scheduler for repeated scenario execution.

        :param event: The ConfigLoadedEvent containing the loaded configuration.
        """
        self._global_config = event.config

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        """
        Handle the event when arguments are being parsed, adding repeater-related arguments.

        This method adds command-line options for controlling the number of scenario
        repetitions, the delay between repetitions, and the fail-fast behavior.

        :param event: The ArgParseEvent containing the argument parser.
        """
        group = event.arg_parser.add_argument_group("Repeater")
        help_message = ("Number of times to repeat scenarios (default: 1). "
                        "The resulting scenario status will be failed if any repeat fail")
        group.add_argument("-N", "--repeats", type=int, default=self._repeats, help=help_message)
        group.add_argument("--repeats-delay", type=float, default=self._repeats_delay,
                           help="Delay in seconds between scenario repeats (default: 0.0s)")
        group.add_argument("--fail-fast-on-repeat", action="store_true", default=self._fail_fast,
                           help="Stop repeating scenarios after the first failure")

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        """
        Handle the event after arguments have been parsed, applying repetition settings.

        This method processes the parsed arguments and applies them to configure the
        number of repetitions, delay, and fail-fast behavior. It raises errors if
        invalid combinations of arguments are provided.

        :param event: The ArgParsedEvent containing the parsed arguments.
        :raises ValueError: If invalid values are provided for repeats or delay.
        """
        self._repeats = event.args.repeats
        self._repeats_delay = event.args.repeats_delay
        self._fail_fast = event.args.fail_fast_on_repeat

        if self._repeats < 1:
            raise ValueError("--repeats must be >= 1")

        if self._repeats_delay < 0.0:
            raise ValueError("--repeats-delay must be >= 0.0")

        if (self._repeats_delay > 0.0) and (self._repeats <= 1):
            raise ValueError("--repeats-delay must be used with --repeats > 1")

        if self._fail_fast and (self._repeats <= 1):
            raise ValueError("--fail-fast-on-repeat must be used with --repeats > 1")

        if self._is_repeating_enabled():
            assert self._global_config is not None  # for type checking
            self._global_config.Registry.ScenarioScheduler.register(self._scheduler_factory, self)

    def on_startup(self, event: StartupEvent) -> None:
        """
        Handle the startup event, storing the scenario scheduler.

        This method captures the scenario scheduler from the startup event,
        enabling it to manage scheduling of repeated scenarios.

        :param event: The StartupEvent instance signaling system startup.
        """
        self._scheduler = event.scheduler

    async def on_scenario_execute(self,
                                  event: Union[ScenarioRunEvent, ScenarioSkippedEvent]) -> None:
        """
        Handle the event when a scenario is executed or skipped, managing repetitions.

        This method ensures that if a scenario is repeated, a delay is applied
        between repetitions if configured. It also checks for fail-fast behavior
        to stop repetitions after the first failure.

        :param event: The ScenarioRunEvent or ScenarioSkippedEvent instance.
        :raises RepeaterExecutionInterrupted: If fail-fast behavior is triggered.
        """
        if not self._is_repeating_enabled():
            return

        if self._fail_fast and (self._failed_count > 0):
            raise RepeaterExecutionInterrupted("Stop repeating scenarios after the first failure")

        scenario = event.scenario_result.scenario
        if (self._repeat_scenario_id == scenario.unique_id) and (self._repeats_delay > 0.0):
            await self._sleep(self._repeats_delay)

    async def on_scenario_end(self,
                              event: Union[ScenarioPassedEvent, ScenarioFailedEvent]) -> None:
        """
        Handle the event when a scenario ends, scheduling additional repetitions if necessary.

        This method tracks scenario results and schedules additional repetitions
        if the scenario has not been repeated the configured number of times. It also
        updates the count of failed scenarios.

        :param event: The ScenarioPassedEvent or ScenarioFailedEvent instance.
        """
        if not self._is_repeating_enabled():
            return
        assert isinstance(self._scheduler, ScenarioScheduler)  # for type checking

        scenario = event.scenario_result.scenario
        if scenario.unique_id != self._repeat_scenario_id:
            self._repeat_scenario_id = scenario.unique_id
            self._failed_count = 1 if event.scenario_result.is_failed() else 0
            for _ in range(self._repeats - 1):
                self._scheduler.schedule(scenario)
        else:
            if event.scenario_result.is_failed():
                self._failed_count += 1

    def on_cleanup(self, event: CleanupEvent) -> None:
        """
        Handle the cleanup event, adding a summary of the repetition process.

        This method generates a summary message detailing how many times scenarios
        were repeated and whether delays were applied between repetitions.

        :param event: The CleanupEvent signaling the end of execution.
        """
        if not self._is_repeating_enabled():
            return

        if not event.report.interrupted:
            message = self._get_summary_message()
            event.report.add_summary(message)

    def _is_repeating_enabled(self) -> bool:
        """
        Check if scenario repetition is enabled.

        :return: True if repetitions are enabled, False otherwise.
        """
        return self._repeats > 1

    def _get_summary_message(self) -> str:
        """
        Generate a summary message for the repetition process.

        This method returns a string summarizing the repetition settings,
        including the number of repetitions and any delays applied.

        :return: A string summarizing the repetition process.
        """
        message = f"repeated x{self._repeats}"
        if self._repeats_delay > 0.0:
            message += f" with delay {self._repeats_delay!r}s"
        return message


class Repeater(PluginConfig):
    """
    Configuration class for the RepeaterPlugin.

    This class defines the configuration options for the RepeaterPlugin, including
    the scheduler factory used for managing repeated scenario executions.
    """
    plugin = RepeaterPlugin
    description = "Repeat scenarios a specified number of times"

    # Scheduler that will be used to create aggregated result for repeated scenarios
    scheduler_factory: Type[ScenarioScheduler] = RepeaterScenarioScheduler
