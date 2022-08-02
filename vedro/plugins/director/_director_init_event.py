from typing import TYPE_CHECKING, Any

from vedro.core import Event

DirectorPlugin = Any
if TYPE_CHECKING:  # pragma: no cover
    from ._director import DirectorPlugin

__all__ = ("DirectorInitEvent",)


class DirectorInitEvent(Event):
    def __init__(self, director: DirectorPlugin) -> None:
        self._director = director

    @property
    def director(self) -> DirectorPlugin:
        return self._director

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._director!r})"
