import os
from argparse import ArgumentParser, Namespace
from pathlib import Path
from time import monotonic_ns
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Type

import pytest
from niltype import Nil, Nilable

from vedro import Scenario
from vedro.core import Config, Dispatcher, VirtualScenario, get_scenario_meta
from vedro.events import ArgParsedEvent, ArgParseEvent, ConfigLoadedEvent
from vedro.plugins.skipper import Skipper, SkipperPlugin
from vedro.plugins.skipper import only as only_scenario
from vedro.plugins.skipper import skip as skip_scenario


@pytest.fixture()
def dispatcher() -> Dispatcher:
    return Dispatcher()


@pytest.fixture()
def skipper(dispatcher: Dispatcher) -> SkipperPlugin:
    tagger = SkipperPlugin(Skipper)
    tagger.subscribe(dispatcher)
    return tagger


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        Path("./scenarios").mkdir(exist_ok=True)
        yield tmp_path
    finally:
        os.chdir(cwd)


async def fire_arg_parsed_event(dispatcher: Dispatcher, *,
                                file_or_dir: Optional[List[str]] = None,
                                ignore: Optional[List[str]] = None,
                                subject: Optional[str] = None,
                                project_dir: Optional[Path] = None) -> None:
    project_dir_ = project_dir if project_dir else Config.project_dir

    class CustomConfig(Config):
        project_dir = project_dir_

    await dispatcher.fire(ConfigLoadedEvent(Path(), CustomConfig))

    arg_parse_event = ArgParseEvent(ArgumentParser())
    await dispatcher.fire(arg_parse_event)

    if file_or_dir is None:
        file_or_dir = ["."]
    if ignore is None:
        ignore = []
    namespace = Namespace(subject=subject, file_or_dir=file_or_dir, ignore=ignore,
                          exp_selective_discoverer=False)

    arg_parsed_event = ArgParsedEvent(namespace)
    await dispatcher.fire(arg_parsed_event)


def _make_vscenario(path: Optional[Path] = None, *,
                    name: str = "Scenario",
                    subject: Optional[str] = None,
                    only: bool = False,
                    skip: bool = False,
                    init: Optional[Callable[..., None]] = None) -> Scenario:
    if path is None:
        path = Path(f"scenarios/scenario_{monotonic_ns()}.py").absolute()
    ns = {"__file__": path}
    if subject is not None:
        ns["subject"] = subject
    if init is not None:
        ns["__init__"] = init

    new_scn = type(name, (Scenario,), ns)
    if only:
        only_scenario(new_scn)
    if skip:
        skip_scenario(new_scn)

    return new_scn


def make_vscenario(path: Optional[Path] = None, *,
                   name: str = "Scenario",
                   subject: Optional[str] = None,
                   only: bool = False,
                   skip: bool = False) -> VirtualScenario:
    new_scn = _make_vscenario(path, name=name, subject=subject, only=only, skip=skip)
    vscenario = VirtualScenario(new_scn, steps=[])
    return vscenario


def make_template_vscenario(init: Callable[..., None], *,
                            path: Optional[Path] = None,
                            name: Optional[str] = None,
                            only: bool = False,
                            skip: bool = False) -> Tuple[Scenario, List[VirtualScenario]]:
    name = name if name is not None else f"Scenario_{monotonic_ns()}"
    new_scn = _make_vscenario(path, name=name, only=only, skip=skip, init=init)

    vscenarios = []
    for key, val in getattr(init, "__globals__").items():
        if key.startswith(name):
            vscenarios.append(VirtualScenario(val, steps=[]))
    return new_scn, vscenarios


def touch(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("")
    return path


def get_skipped(scenarios: Iterable[VirtualScenario]) -> List[VirtualScenario]:
    return [scn for scn in scenarios if scn.is_skipped()]


def get_scenarios(key: str, globals_: Dict[str, Any]) -> List[Type[Scenario]]:
    return [scn for name, scn in globals_.items() if name.startswith(key)]


def get_only_attr(scenario: Type[Scenario]) -> bool:
    return get_scenario_meta(scenario, "only", default=False, plugin=SkipperPlugin)


def get_skip_attr(scenario: Type[Scenario]) -> bool:
    return get_scenario_meta(scenario, "skipped", default=False, plugin=SkipperPlugin)


def get_skip_reason_attr(scenario: Type[Scenario]) -> Nilable[str]:
    return get_scenario_meta(scenario, "skip_reason", default=Nil, plugin=SkipperPlugin)
