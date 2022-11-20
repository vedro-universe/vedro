from abc import ABC, abstractmethod
from asyncio import iscoroutinefunction
from heapq import heappop, heappush
from time import monotonic_ns
from typing import Any, Callable, Dict, List, Type

from ._event import Event

__all__ = ("Dispatcher", "Subscriber", "EventHandler",)


HandlerType = Callable[..., Any]


class EventHandler:
    def __init__(self, priority: int, registered_at: int, handler: HandlerType) -> None:
        self._priority = priority
        self._registered_at = registered_at
        self._handler = handler

    async def __call__(self, event: Event) -> None:
        if iscoroutinefunction(self._handler):
            await self._handler(event)
        else:
            self._handler(event)

    def __lt__(self, other: "EventHandler") -> bool:
        assert isinstance(other, EventHandler)
        if self._priority == other._priority:
            return self._registered_at < other._registered_at
        return self._priority < other._priority


# backward compatibility
RegisteredItemType = EventHandler


class Subscriber(ABC):
    @abstractmethod
    def subscribe(self, dispatcher: "Dispatcher") -> None:
        raise NotImplementedError()


class Dispatcher:
    def __init__(self) -> None:
        self._events: Dict[str, List[EventHandler]] = {}

    def register(self, subscriber: "Subscriber") -> None:
        subscriber.subscribe(self)

    def listen(self, event: Type[Event], handler: HandlerType, priority: int = 0) -> "Dispatcher":
        assert issubclass(event, Event), "Event must be a subclass of 'vedro.events.Event'"
        if event.__name__ not in self._events:
            self._events[event.__name__] = []
        heappush(self._events[event.__name__], EventHandler(priority, monotonic_ns(), handler))
        return self

    async def fire(self, event: Event) -> None:
        if event.__class__.__name__ not in self._events:
            return
        registered = self._events[event.__class__.__name__]
        registered_copy: List[EventHandler] = []
        while len(registered) > 0:
            handler = heappop(registered)
            await handler(event)
            heappush(registered_copy, handler)
        self._events[event.__class__.__name__] = registered_copy
