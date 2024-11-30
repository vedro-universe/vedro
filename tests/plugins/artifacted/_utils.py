from argparse import ArgumentParser, Namespace
from collections import deque
from pathlib import Path
from time import monotonic_ns
from typing import Optional
from unittest.mock import patch

import pytest

from vedro import Config as _Config
from vedro import FileArtifact
from vedro import Scenario as VedroScenario
from vedro.core import Dispatcher, VirtualScenario, VirtualStep
from vedro.events import ArgParsedEvent, ArgParseEvent, ConfigLoadedEvent
from vedro.plugins.artifacted import Artifacted, ArtifactedPlugin, ArtifactManager, MemoryArtifact


@pytest.fixture()
def dispatcher() -> Dispatcher:
    return Dispatcher()


@pytest.fixture()
def global_artifacts() -> deque:
    return deque()


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
def artifacts_dir(project_dir: Path):
    artifacts_dir = project_dir / "artifacts/"
    artifacts_dir.mkdir(exist_ok=True)
    return artifacts_dir


@pytest.fixture()
def artifact_manager(artifacts_dir: Path, project_dir: Path):
    return ArtifactManager(artifacts_dir, project_dir)


@pytest.fixture()
def artifacted(dispatcher: Dispatcher,
               global_artifacts: deque,
               scenario_artifacts: deque,
               step_artifacts: deque) -> ArtifactedPlugin:
    artifacted = ArtifactedPlugin(Artifacted,
                                  global_artifacts=global_artifacts,
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
                                save_artifacts: bool = Artifacted.save_artifacts,
                                add_artifact_details: bool = Artifacted.add_artifact_details,
                                artifacts_dir: Optional[Path] = None) -> None:
    await dispatcher.fire(ArgParseEvent(ArgumentParser()))

    namespace = Namespace(
        save_artifacts=save_artifacts,
        add_artifact_details=add_artifact_details,
        artifacts_dir=artifacts_dir,
    )
    await dispatcher.fire(ArgParsedEvent(namespace))


def patch_rmtree(exception: Optional[Exception] = None):
    return patch("shutil.rmtree", side_effect=exception)


def patch_copy2(exception: Optional[Exception] = None):
    return patch("shutil.copy2", side_effect=exception)


def patch_write_bytes(exception: Optional[Exception] = None):
    return patch("pathlib.Path.write_bytes", side_effect=exception)


def patch_mkdir(exception: Optional[Exception] = None):
    return patch("pathlib.Path.mkdir", side_effect=exception)
