from asyncio import iscoroutinefunction
from collections import deque
from typing import Any, Callable, Deque, Dict, Tuple, Union

from vedro.core import Dispatcher, Plugin
from vedro.events import ScenarioFailedEvent, ScenarioPassedEvent, ScenarioRunEvent

__all__ = ("Deferrer", "defer", "Deferrable",)


Deferrable = Tuple[Callable[..., Any], Tuple[Any, ...], Dict[str, Any]]

_queue: Deque[Deferrable] = deque()


def defer(fn: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
    _queue.append((fn, args, kwargs))


class Deferrer(Plugin):
    def __init__(self, queue: Deque[Deferrable] = _queue) -> None:
        super().__init__()
        self._queue = queue

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ScenarioRunEvent, self.on_scenario_run) \
                  .listen(ScenarioPassedEvent, self.on_scenario_end) \
                  .listen(ScenarioFailedEvent, self.on_scenario_end)

    def on_scenario_run(self, event: ScenarioRunEvent) -> None:
        self._queue.clear()

    async def on_scenario_end(self,
                              event: Union[ScenarioPassedEvent, ScenarioFailedEvent]) -> None:
        while len(self._queue) > 0:
            fn, args, kwargs = self._queue.pop()
            if iscoroutinefunction(fn):
                await fn(*args, **kwargs)
            else:
                fn(*args, **kwargs)
