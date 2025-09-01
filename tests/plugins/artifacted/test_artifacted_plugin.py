from collections import deque
from os import linesep
from pathlib import Path
from unittest.mock import Mock, call

import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro.core import AggregatedResult, Dispatcher, Report, ScenarioResult, StepResult
from vedro.events import (
    CleanupEvent,
    ScenarioFailedEvent,
    ScenarioPassedEvent,
    ScenarioReportedEvent,
    ScenarioRunEvent,
    StepFailedEvent,
    StepPassedEvent,
)
from vedro.plugins.artifacted import ArtifactManager

from ._utils import (
    artifacted,
    artifacts_dir,
    create_file_artifact,
    create_memory_artifact,
    dispatcher,
    fire_arg_parsed_event,
    fire_config_loaded_event,
    global_artifacts,
    make_artifacted_plugin,
    make_vscenario,
    make_vstep,
    project_dir,
    scenario_artifacts,
    step_artifacts,
)

__all__ = ("dispatcher", "global_artifacts", "scenario_artifacts", "step_artifacts",
           "artifacted", "project_dir", "artifacts_dir")  # fixtures


async def test_arg_parsed_event_with_artifacts_dir_created(*, dispatcher: Dispatcher,
                                                           project_dir: Path,
                                                           artifacts_dir: Path):
    with given:
        artifact_manager_ = Mock(spec_set=ArtifactManager)
        make_artifacted_plugin(artifact_manager_).subscribe(dispatcher)

        await fire_config_loaded_event(dispatcher, project_dir)

    with when:
        await fire_arg_parsed_event(dispatcher, artifacts_dir=artifacts_dir)

    with then:
        assert artifact_manager_.mock_calls == [call.cleanup_artifacts()]


@pytest.mark.usefixtures(artifacted.__name__)
async def test_arg_parsed_event_error_on_disabled_artifact_saving(*, dispatcher: Dispatcher,
                                                                  project_dir: Path,
                                                                  artifacts_dir: Path):
    with given:
        await fire_config_loaded_event(dispatcher, project_dir)

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
        await fire_arg_parsed_event(dispatcher, artifacts_dir=artifacts_dir)

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


async def test_scenario_reported_event_saves_scenario_artifacts(*, dispatcher: Dispatcher,
                                                                project_dir: Path):
    with given:
        artifact_manager_ = Mock(spec_set=ArtifactManager)
        make_artifacted_plugin(artifact_manager_).subscribe(dispatcher)

        await fire_config_loaded_event(dispatcher, project_dir)
        await fire_arg_parsed_event(dispatcher)

        scenario_result = ScenarioResult(make_vscenario())
        scenario_result.set_started_at(3.14)  # started_at is used in _get_scenario_artifacts_dir
        scenario_result.attach(artifact1 := create_memory_artifact())
        scenario_result.attach(artifact2 := create_file_artifact(project_dir / "test.txt"))

        aggregated_result = AggregatedResult.from_existing(scenario_result, [scenario_result])
        event = ScenarioReportedEvent(aggregated_result)

        artifact_manager_.reset_mock()
        artifact_manager_.save_artifact = Mock(
            side_effect=[
                Path(project_dir / artifact1.name),
                Path(project_dir / artifact2.name)
            ]
        )

    with when:
        await dispatcher.fire(event)

    with then:
        scn_artifacts_path = project_dir / ".vedro/artifacts/scenarios/scenario/3-14-Scenario-0"

        assert artifact_manager_.mock_calls == [
            call.save_artifact(artifact1, scn_artifacts_path),
            call.save_artifact(artifact2, scn_artifacts_path),
        ]


async def test_scenario_reported_event_saves_step_artifacts(*, dispatcher: Dispatcher,
                                                            project_dir: Path):
    with given:
        artifact_manager_ = Mock(spec_set=ArtifactManager)
        make_artifacted_plugin(artifact_manager_).subscribe(dispatcher)

        await fire_config_loaded_event(dispatcher, project_dir)
        await fire_arg_parsed_event(dispatcher)

        step_result = StepResult(make_vstep())
        step_result.attach(artifact1 := create_memory_artifact())
        step_result.attach(artifact2 := create_file_artifact(project_dir / "test.txt"))

        scenario_result = ScenarioResult(make_vscenario())
        scenario_result.set_started_at(3.14)
        scenario_result.add_step_result(step_result)

        aggregated_result = AggregatedResult.from_existing(scenario_result, [scenario_result])
        event = ScenarioReportedEvent(aggregated_result)

        artifact_manager_.reset_mock()
        artifact_manager_.save_artifact = Mock(
            side_effect=[
                Path(project_dir / artifact1.name),
                Path(project_dir / artifact2.name)
            ]
        )

    with when:
        await dispatcher.fire(event)

    with then:
        scn_artifacts_path = project_dir / ".vedro/artifacts/scenarios/scenario/3-14-Scenario-0"

        assert artifact_manager_.mock_calls == [
            call.save_artifact(artifact1, project_dir / scn_artifacts_path),
            call.save_artifact(artifact2, project_dir / scn_artifacts_path),
        ]


async def test_cleanup_event_saves_global_artifacts(*, dispatcher: Dispatcher, project_dir: Path):
    with given:
        artifact_manager_ = Mock(spec_set=ArtifactManager)
        make_artifacted_plugin(artifact_manager_).subscribe(dispatcher)

        await fire_config_loaded_event(dispatcher, project_dir)
        await fire_arg_parsed_event(dispatcher)

        report = Report()
        report.attach(artifact1 := create_memory_artifact())
        report.attach(artifact2 := create_file_artifact(project_dir / "test.txt"))

        artifact_manager_.reset_mock()
        artifact_manager_.save_artifact = Mock(
            side_effect=[
                Path(project_dir / artifact1.name),
                Path(project_dir / artifact2.name)
            ]
        )

        event = CleanupEvent(report)

    with when:
        await dispatcher.fire(event)

    with then:
        global_artifacts_dir = project_dir / ".vedro/artifacts/global"

        assert artifact_manager_.mock_calls == [
            call.save_artifact(artifact1, project_dir / global_artifacts_dir),
            call.save_artifact(artifact2, project_dir / global_artifacts_dir),
        ]

        assert report.summary == [
            linesep.join([
                "global artifacts:",
                f"#   - {artifact1.name}",
                f"#   - {artifact2.name}",
            ])
        ]
