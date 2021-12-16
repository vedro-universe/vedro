import sys
from traceback import format_exception
from typing import Any, Dict, TextIO

from vedro.core import Dispatcher, ExcInfo, ScenarioResult
from vedro.events import (
    ScenarioFailedEvent,
    ScenarioPassedEvent,
    ScenarioRunEvent,
    ScenarioSkippedEvent,
)

from .._reporter import Reporter

__all__ = ("PyCharmReporter",)


class PyCharmReporter(Reporter):
    def __init__(self, out: TextIO = sys.stdout) -> None:
        self._out = out

    @property
    def name(self) -> str:
        return "pycharm"

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ScenarioRunEvent, self.on_scenario_run) \
                  .listen(ScenarioPassedEvent, self.on_scenario_passed) \
                  .listen(ScenarioFailedEvent, self.on_scenario_failed) \
                  .listen(ScenarioSkippedEvent, self.on_scenario_skipped)

    def on_scenario_run(self, event: ScenarioRunEvent) -> None:
        scenario_result: ScenarioResult = event.scenario_result
        self._write_message("testStarted", {
            "name": scenario_result.scenario.subject,
        })

    def on_scenario_passed(self, event: ScenarioPassedEvent) -> None:
        scenario_result: ScenarioResult = event.scenario_result
        self._write_message("testFinished", {
            "name": scenario_result.scenario.subject,
            "duration": int(scenario_result.elapsed * 1000),
        })

    def on_scenario_failed(self, event: ScenarioFailedEvent) -> None:
        scenario_result: ScenarioResult = event.scenario_result

        message = ""
        for step_result in scenario_result.step_results:
            if step_result.exc_info:
                message += self._format_exception(step_result.exc_info)

        self._write_message("testFailed", {
            "name": scenario_result.scenario.subject,
            "duration": int(scenario_result.elapsed * 1000),
            "message": message,
        })

    def on_scenario_skipped(self, event: ScenarioSkippedEvent) -> None:
        scenario_result: ScenarioResult = event.scenario_result
        self._write_message("testIgnored", {
            "name": scenario_result.scenario.subject,
        })

    def _format_exception(self, exc_info: ExcInfo) -> str:
        formatted = format_exception(exc_info.type, exc_info.value, exc_info.traceback)
        return "".join(formatted)

    def _escape_value(self, value: str) -> str:
        symbols = {"'": "|'", "\n": "|n", "\r": "|r", "|": "||", "[": "|[", "]": "|]"}
        return value.translate({ord(k): v for k, v in symbols.items()})

    def _write_message(self, name: str, attributes: Dict[str, Any]) -> None:
        message = f"##teamcity[{name}"
        for key, val in attributes.items():
            escaped = self._escape_value(str(val))
            message += f" {key}='{escaped}'"
        message += "]\n"
        self._out.write(message)
