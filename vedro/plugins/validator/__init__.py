from typing import Any, Optional

from ..._core import Dispatcher
from ..._events import ScenarioFailEvent, ScenarioRunEvent
from ..plugin import Plugin

__all__ = ("Validator",)


class Validator(Plugin):
    def __init__(self, validator: Optional[Any] = None) -> None:
        self._validator = validator

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ScenarioRunEvent, self.on_scenario_run) \
                  .listen(ScenarioFailEvent, self.on_scenario_fail)

    def on_scenario_run(self, event: ScenarioRunEvent) -> None:
        event.scenario.set_errors([])

    def on_scenario_fail(self, event: ScenarioFailEvent) -> None:
        if self._validator:
            event.scenario.set_errors(event.scenario.errors + self._validator.errors())
            self._validator.reset()
