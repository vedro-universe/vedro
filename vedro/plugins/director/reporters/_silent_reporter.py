from ...._core import Dispatcher
from .._reporter import Reporter


class SilentReporter(Reporter):
    def __init__(self) -> None:
        pass

    def subscribe(self, dispatcher: Dispatcher) -> None:
        pass
