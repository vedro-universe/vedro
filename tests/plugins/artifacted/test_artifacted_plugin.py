from collections import deque
from time import monotonic_ns
from unittest.mock import Mock

import pytest
from baby_steps import given, then, when

from vedro.core import Dispatcher, Plugin, ScenarioResult, StepResult, VirtualScenario, VirtualStep
from vedro.events import (
    ScenarioFailedEvent,
    ScenarioPassedEvent,
    ScenarioRunEvent,
    StepFailedEvent,
    StepPassedEvent,
)
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
def artifacted(scenario_artifacts: deque, step_artifacts: deque) -> ArtifactedPlugin:
    return ArtifactedPlugin(Artifacted,
                            scenario_artifacts=scenario_artifacts, step_artifacts=step_artifacts)


def create_artifact() -> MemoryArtifact:
    return MemoryArtifact(f"test-{monotonic_ns()}", "text/plain", b"")


def test_artifacted_plugin():
    with when:
        plugin = ArtifactedPlugin(Artifacted)

    with then:
        assert isinstance(plugin, Plugin)


@pytest.mark.asyncio
async def test_artifacted_scenario_run_event(*, dispatcher: Dispatcher,
                                             artifacted: ArtifactedPlugin,
                                             scenario_artifacts: deque, step_artifacts: deque):
    with given:
        artifacted.subscribe(dispatcher)

        scenario_result = ScenarioResult(Mock(VirtualScenario))
        event = ScenarioRunEvent(scenario_result)

        scenario_artifacts.append(create_artifact())
        step_artifacts.append(create_artifact())

    with when:
        await dispatcher.fire(event)

    with then:
        assert len(scenario_artifacts) == 0
        assert len(step_artifacts) == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("event_class", [ScenarioPassedEvent, ScenarioFailedEvent])
async def test_artifacted_scenario_end_event(event_class, *, dispatcher: Dispatcher,
                                             artifacted: ArtifactedPlugin,
                                             scenario_artifacts: deque):
    with given:
        artifacted.subscribe(dispatcher)
        scenario_result = ScenarioResult(Mock(VirtualScenario))
        event = event_class(scenario_result)

        artifact1 = create_artifact()
        scenario_artifacts.append(artifact1)

        artifact2 = create_artifact()
        scenario_artifacts.append(artifact2)

    with when:
        await dispatcher.fire(event)

    with then:
        assert scenario_result.artifacts == [artifact1, artifact2]


@pytest.mark.asyncio
@pytest.mark.parametrize("event_class", [StepPassedEvent, StepFailedEvent])
async def test_artifacted_step_end_event(event_class, *, dispatcher: Dispatcher,
                                         artifacted: ArtifactedPlugin,
                                         step_artifacts: deque):
    with given:
        artifacted.subscribe(dispatcher)
        step_result = StepResult(Mock(VirtualStep))
        event = event_class(step_result)

        artifact1 = create_artifact()
        step_artifacts.append(artifact1)

        artifact2 = create_artifact()
        step_artifacts.append(artifact2)

    with when:
        await dispatcher.fire(event)

    with then:
        assert step_result.artifacts == [artifact1, artifact2]
