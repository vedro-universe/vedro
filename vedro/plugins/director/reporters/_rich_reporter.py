import json
import os
import shutil
from time import monotonic
from traceback import format_exception
from typing import Union

from rich.console import Console
from rich.style import Style

from ...._core import Dispatcher
from ...._core._virtual_scenario import VirtualScenario
from ...._events import (
    CleanupEvent,
    ScenarioFailEvent,
    ScenarioPassEvent,
    ScenarioRunEvent,
    ScenarioSkipEvent,
    StartupEvent,
)
from .._reporter import Reporter


class RichReporter(Reporter):
    def __init__(self, verbosity: int) -> None:
        super().__init__()
        self._verbosity = verbosity
        size = self._get_terminal_size()
        self._console = Console(
            highlight=False,
            force_terminal=True,
            markup=False,
            emoji=False,
            width=size.columns,
            height=size.lines,
        )
        self._namespace: Union[str, None] = None
        self._start_time = 0.0
        self._total = 0
        self._passed = 0
        self._failed = 0
        self._skipped = 0

    def _get_terminal_size(self) -> os.terminal_size:
        columns, lines = shutil.get_terminal_size()
        # Fix columns=0 lines=0 in Pycharm
        if columns <= 0:
            columns = 80
        if lines <= 0:
            lines = 24
        return os.terminal_size((columns, lines))

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(StartupEvent, self.on_startup) \
                  .listen(ScenarioRunEvent, self.on_scenario_run) \
                  .listen(ScenarioSkipEvent, self.on_scenario_skip) \
                  .listen(ScenarioPassEvent, self.on_scenario_pass) \
                  .listen(ScenarioFailEvent, self.on_scenario_fail) \
                  .listen(CleanupEvent, self.on_cleanup)

    def on_startup(self, event: StartupEvent) -> None:
        self._start_time = monotonic()
        self._console.print("Scenarios")

    def on_scenario_skip(self, event: ScenarioSkipEvent) -> None:
        self._skipped += 1

    def _format_subject(self, scenario: VirtualScenario) -> str:
        subject = scenario.subject
        if subject and isinstance(subject, str):
            scope = scenario.scope
            return subject.format(**scope.__dict__)
        return scenario.filename.replace("_", " ")

    def on_scenario_run(self, event: ScenarioRunEvent) -> None:
        self._total += 1

        namespace = event.scenario.namespace
        namespace = namespace.replace("_", " ").replace("/", " / ")
        if namespace != self._namespace:
            self._namespace = namespace
            self._console.print(f"* {namespace}", style=Style(bold=True))

    def on_scenario_pass(self, event: ScenarioPassEvent) -> None:
        self._passed += 1
        subject = self._format_subject(event.scenario)

        self._console.print(f" ✔ {subject}", style=Style(color="green"))

    def on_scenario_fail(self, event: ScenarioFailEvent) -> None:
        self._failed += 1

        subject = self._format_subject(event.scenario)
        self._console.print(f" ✗ {subject}", style=Style(color="red"))

        if self._verbosity > 0:
            for step in event.scenario.get_steps():
                if step.is_passed():
                    self._console.print(f"    ✔ {step.name}", style=Style(color="green"))
                elif step.is_failed():
                    self._console.print(f"    ✗ {step.name}", style=Style(color="red"))

        if self._verbosity > 1:
            tb = format_exception(*event.scenario.exception)
            self._console.print("".join(tb), style=Style(color="yellow"))
            if event.scenario.errors:
                errors = " - " + "\n - ".join(event.scenario.errors)
                self._console.print(errors, style=Style(color="yellow"))
            self._console.print()

        if self._verbosity > 2:
            scope = event.scenario.scope
            if scope.__dict__:
                self._console.print("Scope:", style=Style(color="blue", bold=True))
                for key, val in scope.__dict__.items():
                    self._console.print(f" {key}: ", end="", style=Style(color="blue"))
                    try:
                        val_repr = json.dumps(val, ensure_ascii=False, indent=4)
                    except Exception:
                        val_repr = repr(val)
                    self._console.print(val_repr)
                self._console.print()

    def on_cleanup(self, event: CleanupEvent) -> None:
        elapsed = monotonic() - self._start_time
        if self._failed == 0 and self._passed > 0:
            style = Style(color="green", bold=True)
        else:
            style = Style(color="red", bold=True)
        self._console.print()
        self._console.print(f"# {self._total} scenarios, "
                            f"{self._failed} failed, "
                            f"{self._skipped} skipped ",
                            style=style,
                            end="")
        self._console.print(f"({elapsed:.2f}s)", style=Style(color="blue"))
