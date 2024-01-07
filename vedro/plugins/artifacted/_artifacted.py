import shutil
from collections import deque
from pathlib import Path
from typing import Deque, Type, Union

from vedro.core import (
    Artifact,
    ConfigType,
    Dispatcher,
    FileArtifact,
    MemoryArtifact,
    Plugin,
    PluginConfig,
    ScenarioResult,
    StepResult,
)
from vedro.events import (
    ArgParsedEvent,
    ArgParseEvent,
    ConfigLoadedEvent,
    ScenarioFailedEvent,
    ScenarioPassedEvent,
    ScenarioReportedEvent,
    ScenarioRunEvent,
    StepFailedEvent,
    StepPassedEvent,
)

__all__ = ("Artifacted", "ArtifactedPlugin",
           "attach_artifact", "attach_step_artifact", "attach_scenario_artifact",)


_scenario_artifacts: Deque[Artifact] = deque()
_step_artifacts: Deque[Artifact] = deque()


def attach_scenario_artifact(artifact: Artifact) -> None:
    _scenario_artifacts.append(artifact)


def attach_step_artifact(artifact: Artifact) -> None:
    _step_artifacts.append(artifact)


def attach_artifact(artifact: Artifact) -> None:
    attach_step_artifact(artifact)


class ArtifactedPlugin(Plugin):
    def __init__(self, config: Type["Artifacted"], *,
                 scenario_artifacts: Deque[Artifact] = _scenario_artifacts,
                 step_artifacts: Deque[Artifact] = _step_artifacts) -> None:
        super().__init__(config)
        self._scenario_artifacts = scenario_artifacts
        self._step_artifacts = step_artifacts
        self._save_artifacts = config.save_artifacts
        self._artifacts_dir = config.artifacts_dir
        self._add_artifact_details = config.add_artifact_details
        self._global_config: Union[ConfigType, None] = None

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ConfigLoadedEvent, self.on_config_loaded) \
                  .listen(ArgParseEvent, self.on_arg_parse) \
                  .listen(ArgParsedEvent, self.on_arg_parsed) \
                  .listen(ScenarioRunEvent, self.on_scenario_run) \
                  .listen(StepPassedEvent, self.on_step_end) \
                  .listen(StepFailedEvent, self.on_step_end) \
                  .listen(ScenarioPassedEvent, self.on_scenario_end) \
                  .listen(ScenarioFailedEvent, self.on_scenario_end) \
                  .listen(ScenarioReportedEvent, self.on_scenario_reported)

    def on_config_loaded(self, event: ConfigLoadedEvent) -> None:
        self._global_config = event.config

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        group = event.arg_parser.add_argument_group("Artifacted")

        group.add_argument("--save-artifacts", action="store_true",
                           default=self._save_artifacts,
                           help="Save artifacts to the file system")
        group.add_argument("--artifacts-dir", type=Path, default=None,
                           help=("Specify the directory path for saving artifacts "
                                 f"(default: '{self._artifacts_dir}')"))

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        self._save_artifacts = event.args.save_artifacts
        if not self._save_artifacts:
            if event.args.artifacts_dir is not None:
                raise ValueError(
                    "Artifacts directory cannot be specified when artifact saving is disabled")
            return
        self._artifacts_dir = event.args.artifacts_dir or self._artifacts_dir

        project_dir = self._get_project_dir()
        if not self._artifacts_dir.is_absolute():
            self._artifacts_dir = (project_dir / self._artifacts_dir).resolve()
        if not self._is_relative_to(self._artifacts_dir, project_dir):
            raise ValueError(f"Artifacts directory '{self._artifacts_dir}' "
                             f"must be within the project directory '{project_dir}'")

        if self._artifacts_dir.exists():
            shutil.rmtree(self._artifacts_dir)

    def on_scenario_run(self, event: ScenarioRunEvent) -> None:
        self._scenario_artifacts.clear()
        self._step_artifacts.clear()

    async def on_step_end(self, event: Union[StepPassedEvent, StepFailedEvent]) -> None:
        while len(self._step_artifacts) > 0:
            artifact = self._step_artifacts.popleft()
            event.step_result.attach(artifact)

    async def on_scenario_end(self,
                              event: Union[ScenarioPassedEvent, ScenarioFailedEvent]) -> None:
        while len(self._scenario_artifacts) > 0:
            artifact = self._scenario_artifacts.popleft()
            event.scenario_result.attach(artifact)

    async def on_scenario_reported(self, event: ScenarioReportedEvent) -> None:
        if not self._save_artifacts:
            return

        aggregated_result = event.aggregated_result
        for scenario_result in aggregated_result.scenario_results:
            scenario_artifacts_dir = self._get_scenario_artifacts_dir(scenario_result)

            for step_result in scenario_result.step_results:
                for artifact in step_result.artifacts:
                    artifact_path = self._save_artifact(artifact, scenario_artifacts_dir)
                    self._add_extra_details(step_result, artifact_path)

            for artifact in scenario_result.artifacts:
                artifact_path = self._save_artifact(artifact, scenario_artifacts_dir)
                self._add_extra_details(scenario_result, artifact_path)

    def _is_relative_to(self, path: Path, parent: Path) -> bool:
        try:
            path.relative_to(parent)
        except ValueError:
            return False
        else:
            return path != parent

    def _add_extra_details(self, result: Union[ScenarioResult, StepResult],
                           artifact_path: Path) -> None:
        if self._add_artifact_details:
            rel_path = artifact_path.relative_to(self._get_project_dir())
            result.add_extra_details(f"artifact '{rel_path}'")

    def _get_project_dir(self) -> Path:
        assert self._global_config is not None
        return self._global_config.project_dir.resolve()

    def _get_scenario_artifacts_dir(self, scenario_result: ScenarioResult) -> Path:
        scenario = scenario_result.scenario
        scenario_path = self._artifacts_dir / scenario.rel_path.with_suffix('')

        template_index = str(scenario.template_index or 0)
        started_at = str(scenario_result.started_at or 0).replace(".", "-")
        scenario_path /= f"{started_at}-{scenario.name}-{template_index}"

        return scenario_path

    def _save_artifact(self, artifact: Artifact, scenario_path: Path) -> Path:
        if not scenario_path.exists():
            scenario_path.mkdir(parents=True, exist_ok=True)

        if isinstance(artifact, MemoryArtifact):
            artifact_dest_path = (scenario_path / artifact.name).resolve()
            artifact_dest_path.write_bytes(artifact.data)
            return artifact_dest_path

        elif isinstance(artifact, FileArtifact):
            artifact_dest_path = (scenario_path / artifact.name).resolve()
            artifact_source_path = artifact.path
            if not artifact_source_path.is_absolute():
                artifact_source_path = (self._get_project_dir() / artifact_source_path).resolve()
            shutil.copy2(artifact_source_path, artifact_dest_path)
            return artifact_dest_path

        else:
            artifact_type = type(artifact).__name__
            rel_path = scenario_path.relative_to(self._get_project_dir())
            raise TypeError(f"Can't save artifact to '{rel_path}': unknown type '{artifact_type}'")


class Artifacted(PluginConfig):
    plugin = ArtifactedPlugin
    description = "Manages artifacts for step and scenario results"

    # Save artifacts to the file system
    save_artifacts: bool = False

    # Directory path for saving artifacts
    # Available if `save_artifacts` is True
    artifacts_dir: Path = Path(".vedro/artifacts/")

    # Add artifact details to scenario and steps extras
    # Available if `save_artifacts` is True
    add_artifact_details: bool = True
