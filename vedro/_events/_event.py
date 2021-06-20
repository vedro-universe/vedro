from typing import Any, Set, Type

__all__ = ("Event",)


class EventRegistry:
    events: Set[str] = set()

    @classmethod
    def register(cls, event: Type["Event"]) -> None:
        cls.events.add(event.__name__)

    @classmethod
    def is_registered(cls, event: Type["Event"]) -> bool:
        return event.__name__ in cls.events


class Event:
    def __init_subclass__(cls, **kwargs: Any) -> None:
        if EventRegistry.is_registered(cls):
            raise Exception(f"Event {cls} already registered")
        EventRegistry.register(cls)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and (self.__dict__ == other.__dict__)
