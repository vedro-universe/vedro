from argparse import Namespace
from pathlib import Path
from time import monotonic_ns
from typing import Iterable, List, Optional

import pytest

from vedro import Scenario
from vedro.core import ArgumentParser, Dispatcher, VirtualScenario
from vedro.events import ArgParsedEvent, ArgParseEvent
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


async def fire_arg_parsed_event(dispatcher: Dispatcher, *,
                                file_or_dir: Optional[List[str]] = None,
                                ignore: Optional[List[str]] = None,
                                subject: Optional[str] = None) -> None:
    arg_parse_event = ArgParseEvent(ArgumentParser())
    await dispatcher.fire(arg_parse_event)

    if file_or_dir is None:
        file_or_dir = ["."]
    if ignore is None:
        ignore = []
    namespace = Namespace(subject=subject, file_or_dir=file_or_dir, ignore=ignore)

    arg_parsed_event = ArgParsedEvent(namespace)
    await dispatcher.fire(arg_parsed_event)


def make_vscenario(path: Optional[Path] = None, *,
                   subject: Optional[str] = None,
                   only: bool = False,
                   skip: bool = False) -> VirtualScenario:
    scn_subject = subject if subject else None
    path = path if path else Path(f"scenarios/scenario_{monotonic_ns()}.py").absolute()

    class _Scenario(Scenario):
        subject = scn_subject
        __file__ = path

    if only:
        only_scenario(_Scenario)

    if skip:
        skip_scenario(_Scenario)

    vscenario = VirtualScenario(_Scenario, steps=[])
    return vscenario


def touch(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("")
    return path


def get_skipped(scenarios: Iterable[VirtualScenario]) -> List[VirtualScenario]:
    return [scn for scn in scenarios if scn.is_skipped()]
