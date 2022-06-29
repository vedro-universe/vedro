from collections import deque
from pathlib import Path
from time import monotonic_ns

import pytest

from vedro import Scenario
from vedro.core import Dispatcher, VirtualScenario, VirtualStep
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
def artifacted(dispatcher: Dispatcher, scenario_artifacts: deque,
               step_artifacts: deque) -> ArtifactedPlugin:
    artifacted = ArtifactedPlugin(Artifacted,
                                  scenario_artifacts=scenario_artifacts,
                                  step_artifacts=step_artifacts)
    artifacted.subscribe(dispatcher)
    return artifacted


def make_vscenario() -> VirtualScenario:
    class _Scenario(Scenario):
        __file__ = Path(f"scenario_{monotonic_ns()}.py").absolute()

    return VirtualScenario(_Scenario, steps=[])


def make_vstep() -> VirtualStep:
    return VirtualStep(lambda: None)


def create_artifact() -> MemoryArtifact:
    return MemoryArtifact(f"test-{monotonic_ns()}", "text/plain", b"")
