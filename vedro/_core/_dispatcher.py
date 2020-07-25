import inspect
from typing import Any, Callable, Dict, List, Tuple, Type

from .._events import Event

__all__ = ("Dispatcher",)


HandlerType = Callable[..., Any]


class Dispatcher:
    def __init__(self) -> None:
        self._events: Dict[str, List[Tuple[int, HandlerType]]] = {}

    def register(self, subscriber: Any) -> None:  # subscriber: Plugin
        subscriber.subscribe(self)

    def listen(self, event: Type[Event], handler: HandlerType, priority: int = 0) -> "Dispatcher":
        if event.__name__ not in self._events:
            self._events[event.__name__] = []
        self._events[event.__name__].append((priority, handler))
        return self

    async def fire(self, event: Event) -> None:
        if event.__class__.__name__ not in self._events:
            return
        registered = self._events[event.__class__.__name__]
        for priority, handler in sorted(registered, key=lambda x: x[0], reverse=True):
            if inspect.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)
