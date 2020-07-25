from ...._core import Dispatcher
from .._reporter import Reporter


class SilentReporter(Reporter):
    def __init__(self, verbosity: int) -> None:
        self._verbosity = verbosity

    def subscribe(self, dispatcher: Dispatcher) -> None:
        pass
