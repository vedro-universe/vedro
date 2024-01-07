from collections import deque
from pathlib import Path

import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro.core import AggregatedResult, Dispatcher, ScenarioResult, StepResult
from vedro.events import (
    ScenarioFailedEvent,
    ScenarioPassedEvent,
    ScenarioReportedEvent,
    ScenarioRunEvent,
    StepFailedEvent,
    StepPassedEvent,
)
from vedro.plugins.artifacted import (
    Artifact,
    Artifacted,
    ArtifactedPlugin,
    attach_artifact,
    attach_scenario_artifact,
    attach_step_artifact,
)

from ._utils import (
    artifacted,
    create_file_artifact,
    create_memory_artifact,
    dispatcher,
    fire_arg_parsed_event,
    fire_config_loaded_event,
    make_vscenario,
    make_vstep,
    project_dir,
    scenario_artifacts,
    step_artifacts,
)

__all__ = ("dispatcher", "scenario_artifacts", "step_artifacts", "artifacted",
           "project_dir")  # fixtures


@pytest.mark.usefixtures(artifacted.__name__)
async def test_arg_parsed_event_with_artifacts_dir_created(*, dispatcher: Dispatcher,
                                                           project_dir: Path):
    with given:
        await fire_config_loaded_event(dispatcher, project_dir)

        artifacts_dir = project_dir / "artifacts/"
        artifacts_dir.mkdir(exist_ok=True)

    with when:
        await fire_arg_parsed_event(dispatcher, save_artifacts=True, artifacts_dir=artifacts_dir)

    with then:
        assert artifacts_dir.exists() is False


@pytest.mark.usefixtures(artifacted.__name__)
async def test_arg_parsed_event_error_on_disabled_artifact_saving(*, dispatcher: Dispatcher,
                                                                  project_dir: Path):
    with given:
        await fire_config_loaded_event(dispatcher, project_dir)

        artifacts_dir = Path("./artifacts")

    with when, raises(BaseException) as exc:
        await fire_arg_parsed_event(dispatcher, save_artifacts=False, artifacts_dir=artifacts_dir)

    with then:
        assert exc.type is ValueError
        assert str(exc.value) == (
            "Artifacts directory cannot be specified when artifact saving is disabled"
        )


@pytest.mark.usefixtures(artifacted.__name__)
async def test_arg_parsed_event_error_outside_artifacts_dir(*, dispatcher: Dispatcher,
                                                            project_dir: Path):
    with given:
        await fire_config_loaded_event(dispatcher, project_dir)

        artifacts_dir = Path("../artifacts")

    with when, raises(BaseException) as exc:
        await fire_arg_parsed_event(dispatcher, save_artifacts=True, artifacts_dir=artifacts_dir)

    with then:
        assert exc.type is ValueError
        artifacts_dir = (project_dir / artifacts_dir).resolve()
        assert str(exc.value) == (f"Artifacts directory '{artifacts_dir}' must be "
                                  f"within the project directory '{project_dir}'")


@pytest.mark.usefixtures(artifacted.__name__)
async def test_run_event_clears_artifacts(*, dispatcher: Dispatcher, scenario_artifacts: deque,
                                          step_artifacts: deque):
    with given:
        scenario_result = ScenarioResult(make_vscenario())
        event = ScenarioRunEvent(scenario_result)

        scenario_artifacts.append(create_memory_artifact())
        step_artifacts.append(create_memory_artifact())

    with when:
        await dispatcher.fire(event)

    with then:
        assert len(scenario_artifacts) == 0
        assert len(step_artifacts) == 0


@pytest.mark.usefixtures(artifacted.__name__)
@pytest.mark.parametrize("event_class", [ScenarioPassedEvent, ScenarioFailedEvent])
async def test_scenario_end_event_attaches_artifacts(event_class, *, dispatcher: Dispatcher,
                                                     scenario_artifacts: deque):
    with given:
        scenario_result = ScenarioResult(make_vscenario())

        artifact1 = create_memory_artifact()
        scenario_artifacts.append(artifact1)

        artifact2 = create_memory_artifact()
        scenario_artifacts.append(artifact2)

        event = event_class(scenario_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert scenario_result.artifacts == [artifact1, artifact2]


@pytest.mark.usefixtures(artifacted.__name__)
@pytest.mark.parametrize("event_class", [StepPassedEvent, StepFailedEvent])
async def test_step_end_event_attaches_artifacts(event_class, *, dispatcher: Dispatcher,
                                                 step_artifacts: deque):
    with given:
        step_result = StepResult(make_vstep())

        artifact1 = create_memory_artifact()
        step_artifacts.append(artifact1)

        artifact2 = create_memory_artifact()
        step_artifacts.append(artifact2)

        event = event_class(step_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert step_result.artifacts == [artifact1, artifact2]


@pytest.mark.usefixtures(artifacted.__name__)
async def test_scenario_reported_event_saves_scenario_artifacts(*, dispatcher: Dispatcher,
                                                                project_dir: Path):
    with given:
        await fire_config_loaded_event(dispatcher, project_dir)
        await fire_arg_parsed_event(dispatcher, save_artifacts=True)

        scenario_result = ScenarioResult(make_vscenario())
        scenario_result.set_started_at(3.14)

        file_path = project_dir / "test.txt"
        file_content = "text"
        artifact1 = create_memory_artifact(f"{file_content}-1")
        artifact2 = create_file_artifact(file_path, f"{file_content}-2")
        scenario_result.attach(artifact1)
        scenario_result.attach(artifact2)

        aggregated_result = AggregatedResult.from_existing(scenario_result, [scenario_result])
        event = ScenarioReportedEvent(aggregated_result)

    with when:
        await dispatcher.fire(event)

    with then:
        scn_artifacts_path = project_dir / ".vedro/artifacts/scenarios/scenario/3-14-Scenario-0"
        assert scn_artifacts_path.exists()

        artifact1_path = scn_artifacts_path / artifact1.name
        assert artifact1_path.exists()
        assert artifact1_path.read_text() == "text-1"

        artifact2_path = scn_artifacts_path / artifact2.name
        assert artifact2_path.exists()
        assert artifact2_path.read_text() == "text-2"


@pytest.mark.usefixtures(artifacted.__name__)
async def test_scenario_reported_event_saves_step_artifacts(*, dispatcher: Dispatcher,
                                                            project_dir: Path):
    with given:
        await fire_config_loaded_event(dispatcher, project_dir)
        await fire_arg_parsed_event(dispatcher, save_artifacts=True)

        step_result = StepResult(make_vstep())
        artifact = create_memory_artifact(content := "text")
        step_result.attach(artifact)

        scenario_result = ScenarioResult(make_vscenario())
        scenario_result.set_started_at(3.14)
        scenario_result.add_step_result(step_result)

        aggregated_result = AggregatedResult.from_existing(scenario_result, [scenario_result])
        event = ScenarioReportedEvent(aggregated_result)

    with when:
        await dispatcher.fire(event)

    with then:
        scn_artifacts_path = project_dir / ".vedro/artifacts/scenarios/scenario/3-14-Scenario-0"
        assert scn_artifacts_path.exists()

        step_artifacts_path = scn_artifacts_path / artifact.name
        assert step_artifacts_path.exists()
        assert step_artifacts_path.read_text() == content


@pytest.mark.usefixtures(artifacted.__name__)
async def test_scenario_reported_event_incorrect_artifact(*, dispatcher: Dispatcher,
                                                          project_dir: Path):
    with given:
        await fire_config_loaded_event(dispatcher, project_dir)
        await fire_arg_parsed_event(dispatcher, save_artifacts=True)

        scenario_result = ScenarioResult(make_vscenario())
        artifact = type("NewArtifact", (Artifact,), {})()
        scenario_result.attach(artifact)

        aggregated_result = AggregatedResult.from_existing(scenario_result, [scenario_result])
        event = ScenarioReportedEvent(aggregated_result)

    with when, raises(BaseException) as exc:
        await dispatcher.fire(event)

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == (
            "Can't save artifact to '.vedro/artifacts/scenarios/scenario/0-Scenario-0': "
            "unknown type 'NewArtifact'"
        )


@pytest.mark.parametrize("event_class", [ScenarioPassedEvent, ScenarioFailedEvent])
async def test_attach_scenario_artifact(event_class, *, dispatcher: Dispatcher):
    with given:
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
