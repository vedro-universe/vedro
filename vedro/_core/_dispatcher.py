from asyncio import iscoroutinefunction
from heapq import heappop, heappush
from time import monotonic_ns
from typing import Any, Callable, Dict, List, Tuple, Type

from ..events import Event

__all__ = ("Dispatcher", "Subscriber",)


HandlerType = Callable[..., Any]
RegisteredItemType = Tuple[int, int, HandlerType]


class Subscriber:
    def subscribe(self, dispatcher: "Dispatcher") -> None:
        raise NotImplementedError()


class Dispatcher:
    def __init__(self) -> None:
        self._events: Dict[str, List[RegisteredItemType]] = {}

    def register(self, subscriber: "Subscriber") -> None:
        subscriber.subscribe(self)

    def listen(self, event: Type[Event], handler: HandlerType, priority: int = 0) -> "Dispatcher":
        if event.__name__ not in self._events:
            self._events[event.__name__] = []
        heappush(self._events[event.__name__], (priority, monotonic_ns(), handler))
        return self

    async def fire(self, event: Event) -> None:
        if event.__class__.__name__ not in self._events:
            return
        registered = self._events[event.__class__.__name__]
        registered_copy: List[RegisteredItemType] = []
        while len(registered) > 0:
            priority, registered_at, handler = heappop(registered)
            if iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)
            heappush(registered_copy, (priority, registered_at, handler))
        self._events[event.__class__.__name__] = registered_copy
