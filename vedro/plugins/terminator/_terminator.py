import sys
from typing import Any

from ..._core import Dispatcher
from ..._events import CleanupEvent, ScenarioFailEvent, ScenarioPassEvent
from ..plugin import Plugin


class Terminator(Plugin):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._passed = 0
        self._failed = 0

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ScenarioPassEvent, self.on_scenario_pass) \
                  .listen(ScenarioFailEvent, self.on_scenario_fail) \
                  .listen(CleanupEvent, self.on_cleanup, priority=-1)

    def on_scenario_pass(self, event: ScenarioPassEvent) -> None:
        self._passed += 1

    def on_scenario_fail(self, event: ScenarioFailEvent) -> None:
        self._failed += 1

    def on_cleanup(self, event: CleanupEvent) -> None:
        if self._failed > 0 or self._passed == 0:
            sys.exit(1)
        else:
            sys.exit(0)
