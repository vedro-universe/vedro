from asyncio import iscoroutinefunction
from collections import deque
from typing import Any, Callable, Deque, Dict, Tuple, Type, Union, final

from vedro.core import Dispatcher, Plugin, PluginConfig
from vedro.events import (
    CleanupEvent,
    ScenarioFailedEvent,
    ScenarioPassedEvent,
    ScenarioRunEvent,
    StartupEvent,
)

__all__ = ("Deferrer", "DeferrerPlugin", "defer", "defer_global", "Deferrable",)


Deferrable = Tuple[Callable[..., Any], Tuple[Any, ...], Dict[str, Any]]

_queue: Deque[Deferrable] = deque()
_global_queue: Deque[Deferrable] = deque()


def defer(fn: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
    """
    Defer the execution of a function until the end of the current scenario.

    The function will be added to a queue and executed after the scenario completes,
    either successfully or with a failure.

    Deferred functions are executed in the reverse order in which they are added
    (LIFO - Last In, First Out).

    :param fn: The function to be deferred.
    :param args: Positional arguments to be passed to the function.
    :param kwargs: Keyword arguments to be passed to the function.
    """
    _queue.append((fn, args, kwargs))


def defer_global(fn: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
    """
    Defer the execution of a function until the end of the entire test session.

    The function will be added to a global queue and executed after all scenarios have completed.

    :param fn: The function to be deferred.
    :param args: Positional arguments to be passed to the function.
    :param kwargs: Keyword arguments to be passed to the function.
    """
    _global_queue.append((fn, args, kwargs))


@final
class DeferrerPlugin(Plugin):
    """
    A plugin that defers the execution of functions until the end of a scenario or
    the entire test session.

    This plugin listens to scenario events and ensures that deferred functions are executed
    after the scenario has either passed or failed. The deferred functions can be regular
    functions or coroutines. It also supports global deferral of functions to be executed
    at the end of the entire test session.
    """

    def __init__(self, config: Type["Deferrer"], *,
                 queue: Deque[Deferrable] = _queue,
                 global_queue: Deque[Deferrable] = _global_queue) -> None:
        """
        Initialize the DeferrerPlugin with the provided configuration.

        :param config: The Deferrer configuration class.
        :param queue: The queue holding deferred functions.
        :param global_queue: The global queue holding deferred functions for the entire
                             test session.
        """
        super().__init__(config)
        self._queue = queue
        self._global_queue = global_queue

    def subscribe(self, dispatcher: Dispatcher) -> None:
        """
        Subscribe to scenario events for running deferred functions.

        :param dispatcher: The dispatcher to listen to events.
        """
        dispatcher.listen(StartupEvent, self.on_startup) \
                  .listen(ScenarioRunEvent, self.on_scenario_run) \
                  .listen(ScenarioPassedEvent, self.on_scenario_end) \
                  .listen(ScenarioFailedEvent, self.on_scenario_end) \
                  .listen(CleanupEvent, self.on_cleanup)

    def on_startup(self, event: StartupEvent) -> None:
        """
        Handle the event when the test session starts, clearing the global deferred function queue.

        :param event: The StartupEvent instance.
        """
        self._global_queue.clear()

    def on_scenario_run(self, event: ScenarioRunEvent) -> None:
        """
        Handle the event when a scenario run starts, clearing the deferred function queue.

        :param event: The ScenarioRunEvent instance.
        """
        self._queue.clear()

    async def on_scenario_end(self,
                              event: Union[ScenarioPassedEvent, ScenarioFailedEvent]) -> None:
        """
        Handle the event when a scenario ends, executing all deferred functions.

        Deferred functions are executed in reverse order (LIFO). If a deferred function
        is a coroutine, it will be awaited. Otherwise, it will be called as a regular function.

        :param event: The ScenarioPassedEvent or ScenarioFailedEvent instance.
        """
        while len(self._queue) > 0:
            fn, args, kwargs = self._queue.pop()
            if iscoroutinefunction(fn):
                await fn(*args, **kwargs)
            else:
                fn(*args, **kwargs)

    async def on_cleanup(self, event: CleanupEvent) -> None:
        """
        Handle the event when the test session ends, executing all globally deferred functions.

        Globally deferred functions are executed in reverse order (LIFO). If a deferred function
        is a coroutine, it will be awaited. Otherwise, it will be called as a regular function.

        :param event: The CleanupEvent instance.
        """
        while len(self._global_queue) > 0:
            fn, args, kwargs = self._global_queue.pop()
            if iscoroutinefunction(fn):
                await fn(*args, **kwargs)
            else:
                fn(*args, **kwargs)


class Deferrer(PluginConfig):
    """
    Configuration class for the DeferrerPlugin.

    This class defines the default behavior for deferring functions during scenario execution.
    It ensures that functions are executed at the end of each scenario.
    """

    plugin = DeferrerPlugin
    description = "Executes deferred functions at the end of each scenario"
