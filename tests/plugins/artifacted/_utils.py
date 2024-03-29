from argparse import ArgumentParser, Namespace
from collections import deque
from pathlib import Path
from time import monotonic_ns
from typing import Optional

import pytest

from vedro import Config as _Config
from vedro import FileArtifact
from vedro import Scenario as VedroScenario
from vedro.core import Dispatcher, VirtualScenario, VirtualStep
from vedro.events import ArgParsedEvent, ArgParseEvent, ConfigLoadedEvent
from vedro.plugins.artifacted import Artifacted, ArtifactedPlugin, MemoryArtifact


@pytest.fixture()
def dispatcher() -> Dispatcher:
    return Dispatcher()


@pytest.fixture()
def scenario_artifacts() -> deque:
    return deque()


@pytest.fixture()
def step_artifacts() -> deque:
    return deque()


@pytest.fixture()
def project_dir(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture()
def artifacted(dispatcher: Dispatcher, scenario_artifacts: deque,
               step_artifacts: deque) -> ArtifactedPlugin:
    artifacted = ArtifactedPlugin(Artifacted,
                                  scenario_artifacts=scenario_artifacts,
                                  step_artifacts=step_artifacts)
    artifacted.subscribe(dispatcher)
    return artifacted


def make_vscenario(file_path: str = "scenarios/scenario.py") -> VirtualScenario:
    class Scenario(VedroScenario):
        __file__ = Path(file_path).absolute()

    return VirtualScenario(Scenario, steps=[])


def make_vstep() -> VirtualStep:
    return VirtualStep(lambda: None)


def create_memory_artifact(content: str = "text") -> MemoryArtifact:
    return MemoryArtifact(f"test-{monotonic_ns()}.txt", "text/plain", content.encode())


def create_file_artifact(path: Path, content: str = "text") -> FileArtifact:
    path.write_text(content)
    return FileArtifact(f"test-{monotonic_ns()}.txt", "text/plain", path)


async def fire_config_loaded_event(dispatcher: Dispatcher, project_dir_: Path) -> None:
    class Config(_Config):
        project_dir = project_dir_

    await dispatcher.fire(ConfigLoadedEvent(Path(), Config))


async def fire_arg_parsed_event(dispatcher: Dispatcher, *,
                                save_artifacts: bool = False,
                                artifacts_dir: Optional[Path] = None) -> None:
    await dispatcher.fire(ArgParseEvent(ArgumentParser()))

    namespace = Namespace(save_artifacts=save_artifacts, artifacts_dir=artifacts_dir)
    await dispatcher.fire(ArgParsedEvent(namespace))
