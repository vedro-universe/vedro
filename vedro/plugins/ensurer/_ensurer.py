from inspect import unwrap
from typing import Any, Callable, List, Optional, Tuple, Type, Union, final

from vedro.core import Dispatcher, Plugin, PluginConfig
from vedro.events import StepFailedEvent, StepPassedEvent, StepRunEvent

from ._ensure import AttemptType, DelayType, Ensure, SwallowExceptionType
from ._runtime_config import RuntimeConfig
from ._runtime_config import runtime_config as _runtime_config

__all__ = ("Ensurer", "EnsurerPlugin", "ensure",)


def ensure(*, attempts: Optional[AttemptType] = None,
           delay: Optional[DelayType] = None,
           swallow: Optional[SwallowExceptionType] = None) -> Ensure:
    """
    Decorator to add retry logic to a function or coroutine.

    :param attempts: The maximum number of times the function can be called.
        To run the function and retry once if an exception is raised, set attempts=2.
        To run the function and retry twice, set attempts=3.
        Default value can be configured via Ensurer plugin params.
    :param delay: The delay between attempts, which can be a fixed value or a callable
        returning a value. Default value can be configured via Ensurer plugin params.
    :param swallow: The exception(s) to be caught and retried.
        Default value can be configured via Ensurer plugin params.
    :return: An instance of Ensure configured with the provided or default parameters.
    """
    return Ensure(attempts=attempts or _runtime_config.get_attempts(),
                  delay=delay or _runtime_config.get_delay(),
                  swallow=swallow or _runtime_config.get_swallow(),
                  logger=_runtime_config.get_logger())


@final
class EnsurerPlugin(Plugin):
    """
    A plugin to integrate the Ensure functionality with the Vedro testing framework.

    This plugin sets up runtime configuration and logs the results of each retry attempt
    during test steps.
    """

    def __init__(self, config: Type["Ensurer"], *,
                 runtime_config: RuntimeConfig = _runtime_config) -> None:
        """
        Initialize the EnsurerPlugin with the provided configuration and runtime configuration.

        :param config: The Ensurer configuration class.
        :param runtime_config: The runtime configuration instance.
            Defaults to the module-level runtime_config.
        """
        super().__init__(config)
        self._runtime_config = runtime_config
        self._runtime_config.set_attempts(config.default_attempts)
        self._runtime_config.set_delay(config.default_delay)
        self._runtime_config.set_swallow(config.default_swallow)

        self._show_attempts = config.show_attempts
        if self._show_attempts:
            self._runtime_config.set_logger(self._logger)
        else:
            self._runtime_config.set_logger(None)

        self._attempt_log: List[
            Tuple[Callable[..., Any], AttemptType, Union[BaseException, None]]
        ] = []

    def subscribe(self, dispatcher: Dispatcher) -> None:
        """
        Subscribe to Vedro events for step run, step passed, and step failed.

        :param dispatcher: The dispatcher to listen to events.
        """
        dispatcher.listen(StepRunEvent, self.on_step_run) \
                  .listen(StepPassedEvent, self.on_step_end) \
                  .listen(StepFailedEvent, self.on_step_end)

    def on_step_run(self, event: StepRunEvent) -> None:
        """
        Handle the event when a step run starts.

        :param event: The StepRunEvent instance.
        """
        self._attempt_log.clear()

    def on_step_end(self, event: Union[StepPassedEvent, StepFailedEvent]) -> None:
        """
        Handle the event when a step ends, logging the results if configured to show attempts.

        :param event: The StepPassedEvent or StepFailedEvent instance.
        """
        if not self._show_attempts:
            return

        for fn, attempt, exc in self._attempt_log:
            if unwrap(fn) == unwrap(event.step_result.step._orig_step):
                extra_details = (f"[{attempt}] attempt failed with {exc!r}" if exc else
                                 f"[{attempt}] attempt succeeded")
                event.step_result.add_extra_details(extra_details)

    def _logger(self, fn: Callable[..., Any],
                attempt: AttemptType,
                exc: Union[BaseException, None]) -> None:
        """
        Log the attempt details including the function, attempt number, and exception.

        :param fn: The function being attempted.
        :param attempt: The attempt number.
        :param exc: The exception raised during the attempt, if any.
        """
        self._attempt_log.append((fn, attempt, exc))


class Ensurer(PluginConfig):
    """
    Configuration class for the EnsurerPlugin.

    This class defines the default settings for the number of attempts, delay between attempts,
    exceptions to swallow, and whether to show attempt logs.
    """

    plugin = EnsurerPlugin
    description = ("Adds configurable retry logic to functions and steps, including attempts, "
                   "delay and exceptions to swallow")

    # Whether to show attempt details in the step results
    # If you are using rich reporter, `--show-steps` must be provided
    show_attempts = True

    # Default number of retry attempts
    default_attempts: AttemptType = 3

    # Default delay between retry attempts
    default_delay: DelayType = 0.0

    # Default exceptions to swallow during retries
    default_swallow: SwallowExceptionType = BaseException
