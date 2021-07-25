import os
import random
import string
import sys
from argparse import Namespace
from pathlib import Path
from types import MethodType, TracebackType
from typing import Any, List, Optional, cast
from unittest.mock import Mock

import pytest
from rich.console import Console

from vedro import Scenario
from vedro.core import (
    Dispatcher,
    ExcInfo,
    Report,
    ScenarioResult,
    StepResult,
    VirtualScenario,
    VirtualStep,
)
from vedro.plugins.director import RichReporter

__all__ = ("dispatcher", "console_", "reporter",
           "make_parsed_args", "make_path", "make_vscenario", "make_vstep",
           "make_scenario_result", "make_step_result", "make_random_name", "make_exc_info",
           "make_report",)


@pytest.fixture()
def dispatcher() -> Dispatcher:
    return Dispatcher()


@pytest.fixture()
def console_() -> Mock:
    return Mock(Console)


@pytest.fixture()
def reporter(console_: Console) -> RichReporter:
    return RichReporter(lambda: console_)


def make_parsed_args(*, verbose: int = 0,
                     show_timings: bool = False,
                     tb_show_locals: bool = False,
                     tb_show_internal_calls: bool = False) -> Namespace:
    return Namespace(
        verbose=verbose,
        show_timings=show_timings,
        tb_show_internal_calls=tb_show_internal_calls,
        tb_show_locals=tb_show_locals,
    )


def make_path(path: str = "", name: str = "scenario.py") -> Path:
    return Path(os.getcwd()) / "scenarios" / path / name


def make_vscenario(*,
                   path: Optional[Path] = None,
                   subject: Optional[str] = None) -> VirtualScenario:
    namespace = {}
    if path:
        namespace["__file__"] = str(path)
    if subject:
        namespace["subject"] = subject
    scenario = type("Scenario", (Scenario,), namespace)

    vscenario = VirtualScenario(scenario, [])
    return vscenario


def make_vstep(*, name: Optional[str] = None) -> VirtualStep:
    def method(self: Any) -> None:
        pass
    if name:
        method.__name__ = name
    return VirtualStep(cast(MethodType, method))


def make_random_name(length: int = 10) -> str:
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))


def make_scenario_result(vscenario: Optional[VirtualScenario] = None,
                         step_results: Optional[List[StepResult]] = None) -> ScenarioResult:
    if vscenario is None:
        vscenario = make_vscenario(subject=make_random_name())
    scenario_result = ScenarioResult(vscenario)

    if step_results:
        for step_result in step_results:
            scenario_result.add_step_result(step_result)
    return scenario_result


def make_step_result(vstep: Optional[VirtualStep] = None) -> StepResult:
    if vstep is None:
        vstep = make_vstep(name=make_random_name())
    step_result = StepResult(vstep)
    return step_result


def make_exc_info(exc_val: Exception) -> ExcInfo:
    try:
        raise exc_val
    except type(exc_val):
        *_, traceback = sys.exc_info()
    return ExcInfo(type(exc_val), exc_val, cast(TracebackType, traceback))


def make_report(scenario_results: Optional[List[ScenarioResult]] = None,
                summaries: Optional[List[str]] = None) -> Report:
    report = Report()
    if scenario_results:
        for scenarior_result in scenario_results:
            report.add_result(scenarior_result)
    if summaries:
        for summary in summaries:
            report.add_summary(summary)
    return report
