from typing import TYPE_CHECKING, Any

from vedro.core import Event

DirectorPlugin = Any
if TYPE_CHECKING:  # pragma: no cover
    from ._director import DirectorPlugin

__all__ = ("DirectorInitEvent",)


class DirectorInitEvent(Event):
    """
    Represents the event fired when the DirectorPlugin is initialized.

    This event allows reporters to register themselves with the DirectorPlugin.
    """

    def __init__(self, director: DirectorPlugin) -> None:
        """
        Initialize the DirectorInitEvent with the specified DirectorPlugin.

        :param director: The instance of the DirectorPlugin.
        """
        self._director = director

    @property
    def director(self) -> DirectorPlugin:
        """
        Get the DirectorPlugin instance that fired this event.

        :return: The DirectorPlugin instance.
        """
        return self._director

    def __repr__(self) -> str:
        """
        Return the string representation of the event.

        :return: The string representation showing the DirectorPlugin.
        """
        return f"{self.__class__.__name__}({self._director!r})"
