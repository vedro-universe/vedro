from pathlib import Path

import pytest
from baby_steps import given, then, when

from vedro.core import Dispatcher, Report, ScenarioResult, StepResult
from vedro.events import (
    CleanupEvent,
    ScenarioFailedEvent,
    ScenarioPassedEvent,
    StepFailedEvent,
    StepPassedEvent,
)
from vedro.plugins.artifacted import (
    Artifacted,
    ArtifactedPlugin,
    attach_artifact,
    attach_global_artifact,
    attach_scenario_artifact,
    attach_step_artifact,
)

from ._utils import (
    create_file_artifact,
    create_memory_artifact,
    dispatcher,
    fire_arg_parsed_event,
    fire_config_loaded_event,
    make_vscenario,
    make_vstep,
    project_dir,
)

__all__ = ("dispatcher",  "project_dir",)  # fixtures


@pytest.mark.parametrize("event_class", [ScenarioPassedEvent, ScenarioFailedEvent])
async def test_attach_scenario_artifact(event_class, *, dispatcher: Dispatcher):
    with given:
        # The ArtifactedPlugin is created directly here to avoid injecting fixtures and
        # focus on testing integration
        artifacted = ArtifactedPlugin(Artifacted)
        artifacted.subscribe(dispatcher)

        artifact = create_memory_artifact()
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

        artifact = create_memory_artifact()
        attach(artifact)

        step_result = StepResult(make_vstep())
        event = event_class(step_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert step_result.artifacts == [artifact]


async def test_attach_global_artifact(dispatcher: Dispatcher, project_dir: Path):
    with given:
        artifacted = ArtifactedPlugin(Artifacted)
        artifacted.subscribe(dispatcher)

        await fire_config_loaded_event(dispatcher, project_dir)
        await fire_arg_parsed_event(dispatcher)

        attach_global_artifact(artifact1 := create_memory_artifact())
        attach_global_artifact(artifact2 := create_file_artifact(project_dir / "test.txt"))

        event = CleanupEvent(report := Report())

    with when:
        await dispatcher.fire(event)

    with then:
        assert report.artifacts == [artifact1, artifact2]
