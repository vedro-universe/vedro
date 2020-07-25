from .._core import Dispatcher


class Plugin:
    def subscribe(self, dispatcher: Dispatcher) -> None:
        raise NotImplementedError()
