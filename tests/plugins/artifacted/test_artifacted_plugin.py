from collections import deque

import pytest
from baby_steps import given, then, when

from vedro.core import Dispatcher, ScenarioResult, StepResult
from vedro.events import (
    ScenarioFailedEvent,
    ScenarioPassedEvent,
    ScenarioRunEvent,
    StepFailedEvent,
    StepPassedEvent,
)
from vedro.plugins.artifacted import (
    Artifacted,
    ArtifactedPlugin,
    attach_artifact,
    attach_scenario_artifact,
    attach_step_artifact,
)

from ._utils import (
    artifacted,
    create_artifact,
    dispatcher,
    make_vscenario,
    make_vstep,
    scenario_artifacts,
    step_artifacts,
)

__all__ = ("dispatcher", "scenario_artifacts", "step_artifacts", "artifacted")  # fixtures


@pytest.mark.usefixtures(artifacted.__name__)
async def test_scenario_run_event(*, dispatcher: Dispatcher, scenario_artifacts: deque,
                                  step_artifacts: deque):
    with given:
        scenario_result = ScenarioResult(make_vscenario())
        event = ScenarioRunEvent(scenario_result)

        scenario_artifacts.append(create_artifact())
        step_artifacts.append(create_artifact())

    with when:
        await dispatcher.fire(event)

    with then:
        assert len(scenario_artifacts) == 0
        assert len(step_artifacts) == 0


@pytest.mark.usefixtures(artifacted.__name__)
@pytest.mark.parametrize("event_class", [ScenarioPassedEvent, ScenarioFailedEvent])
async def test_scenario_end_event(event_class, *, dispatcher: Dispatcher,
                                  scenario_artifacts: deque):
    with given:
        scenario_result = ScenarioResult(make_vscenario())
        event = event_class(scenario_result)

        artifact1 = create_artifact()
        scenario_artifacts.append(artifact1)

        artifact2 = create_artifact()
        scenario_artifacts.append(artifact2)

    with when:
        await dispatcher.fire(event)

    with then:
        assert scenario_result.artifacts == [artifact1, artifact2]


@pytest.mark.usefixtures(artifacted.__name__)
@pytest.mark.parametrize("event_class", [StepPassedEvent, StepFailedEvent])
async def test_step_end_event(event_class, *, dispatcher: Dispatcher, step_artifacts: deque):
    with given:
        step_result = StepResult(make_vstep())
        event = event_class(step_result)

        artifact1 = create_artifact()
        step_artifacts.append(artifact1)

        artifact2 = create_artifact()
        step_artifacts.append(artifact2)

    with when:
        await dispatcher.fire(event)

    with then:
        assert step_result.artifacts == [artifact1, artifact2]


@pytest.mark.parametrize("event_class", [ScenarioPassedEvent, ScenarioFailedEvent])
async def test_attach_scenario_artifact(event_class, *, dispatcher: Dispatcher):
    with given:
        artifacted = ArtifactedPlugin(Artifacted)
        artifacted.subscribe(dispatcher)

        artifact = create_artifact()
        attach_scenario_artifact(artifact)

        scenario_result = ScenarioResult(make_vscenario())
        event = event_class(scenario_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert scenario_result.artifacts == [artifact]


@pytest.mark.parametrize("attach", [attach_artifact, attach_step_artifact])
@pytest.mark.parametrize("event_class", [StepPassedEvent, StepFailedEvent])
async def test_attach_step_artifact(attach, event_class, *, dispatcher: Dispatcher):
    with given:
        artifacted = ArtifactedPlugin(Artifacted)
        artifacted.subscribe(dispatcher)

        artifact = create_artifact()
        attach(artifact)

        step_result = StepResult(make_vstep())
        event = event_class(step_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert step_result.artifacts == [artifact]
