from ...._core import Dispatcher
from .._reporter import Reporter

__all__ = ("SilentReporter",)


class SilentReporter(Reporter):
    def subscribe(self, dispatcher: Dispatcher) -> None:
        pass
