from vedro.core import Plugin

__all__ = ("Reporter",)


class Reporter(Plugin):
    def on_chosen(self) -> None:
        raise NotImplementedError()
