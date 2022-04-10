from abc import abstractmethod

from vedro.core import Plugin

__all__ = ("Reporter",)


class Reporter(Plugin):
    @abstractmethod
    def on_chosen(self) -> None:
        raise NotImplementedError()
