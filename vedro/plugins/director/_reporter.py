from ..._core import Dispatcher


class Reporter:
    def subscribe(self, dispatcher: Dispatcher) -> None:
        raise NotImplementedError()
