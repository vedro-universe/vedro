from typing import Any, Set, Type

__all__ = ("Event",)


class EventRegistry:
    """
    Maintains a registry of all event classes.

    This class provides methods to register new event classes and check if an
    event class is already registered. It ensures that event names are unique
    within the system.
    """

    events: Set[str] = set()

    @classmethod
    def register(cls, event: Type["Event"]) -> None:
        """
        Register a new event class in the registry.

        :param event: The event class to register.
        """
        cls.events.add(event.__name__)

    @classmethod
    def is_registered(cls, event: Type["Event"]) -> bool:
        """
        Check if an event class is already registered.

        :param event: The event class to check.
        :return: True if the event is registered, otherwise False.
        """
        return event.__name__ in cls.events


class Event:
    """
    Serves as a base class for all events.

    This class ensures that every event subclass is uniquely registered
    in the `EventRegistry`. It also provides equality checks based on
    the attributes of the event.
    """

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """
        Perform subclass registration and ensure unique event names.

        :raises RuntimeError: If the event class is already registered.
        """
        if EventRegistry.is_registered(cls):
            raise RuntimeError(f"Event {cls} already registered")
        EventRegistry.register(cls)

    def __eq__(self, other: Any) -> bool:
        """
        Check for equality between two event instances.

        :param other: The object to compare with.
        :return: True if both objects are of the same class and have
                 the same attributes, otherwise False.
        """
        return isinstance(other, self.__class__) and (self.__dict__ == other.__dict__)
