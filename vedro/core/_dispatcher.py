from abc import ABC, abstractmethod
from asyncio import iscoroutinefunction
from heapq import heappop, heappush
from typing import Any, Callable, Dict, List, Type

from ._event import Event

__all__ = ("Dispatcher", "Subscriber", "EventHandler",)


HandlerType = Callable[..., Any]


class EventHandler:
    """
    Manages the registration and invocation of event handlers with priority.

    This class encapsulates an event handler function, its priority, and the
    order of its registration. It allows for asynchronous and synchronous
    execution of the handler function.
    """

    _monotonic_id = 0  # Class-level counter to maintain the order of handler registration

    def __init__(self, priority: int, registered_at: int, handler: HandlerType) -> None:
        """
        Initialize the EventHandler with a given priority, registration time, and handler.

        :param priority: The priority of the handler. Lower values indicate higher priority.
        :param registered_at: The registration time of the handler. Deprecated, not actually used.
        :param handler: The handler function to be called when the event is fired.
        """
        self._priority = priority
        self._handler = handler
        EventHandler._monotonic_id += 1
        self._registered_at = EventHandler._monotonic_id

    async def __call__(self, event: Event) -> None:
        """
        Invoke the handler function with the given event.

        :param event: The event to be passed to the handler function.
        """
        if iscoroutinefunction(self._handler):
            await self._handler(event)
        else:
            self._handler(event)

    def __lt__(self, other: "EventHandler") -> bool:
        """
        Compare two EventHandler instances based on priority and registration order.

        :param other: Another EventHandler instance to compare with.
        :return: True if this instance has higher priority or was registered earlier,
                 otherwise False.
        :raises AssertionError: If 'other' is not an instance of EventHandler.
        """
        if not isinstance(other, EventHandler):
            raise TypeError("Other must be an instance of EventHandler")
        if self._priority == other._priority:
            return self._registered_at < other._registered_at
        return self._priority < other._priority


# backward compatibility
RegisteredItemType = EventHandler


class Subscriber(ABC):
    """
    Defines the interface for subscribers that can subscribe to events.

    This abstract class requires the implementation of the subscribe method,
    which allows subscribers to register themselves with a Dispatcher.
    """

    @abstractmethod
    def subscribe(self, dispatcher: "Dispatcher") -> None:
        """
        Subscribe to the dispatcher's events.

        :param dispatcher: The dispatcher instance to subscribe to.
        """
        pass


class Dispatcher:
    """
    Manages event registration and dispatching to registered handlers.

    This class allows for the registration of event handlers with specific
    priorities and dispatches events to these handlers in the order of their
    priorities.
    """

    def __init__(self) -> None:
        """
        Initialize the Dispatcher with an empty event registry.
        """
        self._events: Dict[str, List[EventHandler]] = {}

    def register(self, subscriber: "Subscriber") -> None:
        """
        Register a subscriber to the dispatcher.

        :param subscriber: The subscriber to be registered.
        """
        subscriber.subscribe(self)

    def listen(self, event: Type[Event], handler: HandlerType, priority: int = 0) -> "Dispatcher":
        """
        Register an event handler for a specific event type.

        :param event: The event type to listen for.
        :param handler: The handler function to be called when the event is fired.
        :param priority: The priority of the handler. Lower values indicate higher priority.
        :return: The Dispatcher instance to allow for method chaining.
        :raises TypeError: If 'event' is not a subclass of 'vedro.events.Event'.
        """
        if not issubclass(event, Event):
            raise TypeError("Event must be a subclass of 'vedro.events.Event'")
        if event.__name__ not in self._events:
            self._events[event.__name__] = []
        # -1 is for backward compatibility
        heappush(self._events[event.__name__], EventHandler(priority, -1, handler))
        return self

    async def fire(self, event: Event) -> None:
        """
        Dispatch the given event to all registered handlers.

        :param event: The event to be dispatched.
        """
        if event.__class__.__name__ not in self._events:
            return
        registered = self._events[event.__class__.__name__]
        registered_copy: List[EventHandler] = []
        while len(registered) > 0:
            handler = heappop(registered)
            await handler(event)
            heappush(registered_copy, handler)
        self._events[event.__class__.__name__] = registered_copy
