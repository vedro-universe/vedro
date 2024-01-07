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
        group.add_argument("--artifacts-dir", type=Path, default=self._artifacts_dir,
                           help=("Specify the directory path for saving artifacts "
                                 f"(default: '{self._artifacts_dir}')"))

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        self._save_artifacts = event.args.save_artifacts
        if not self._save_artifacts and event.args.artifacts_dir != self._artifacts_dir:
            raise ValueError(
                "Artifacts directory cannot be specified when artifact saving is disabled")
        self._artifacts_dir = event.args.artifacts_dir

        project_dir = self._get_project_dir()
        if self._artifacts_dir.is_absolute():
            if not self._artifacts_dir.is_relative_to(project_dir):
                raise ValueError(f"Artifacts directory '{self._artifacts_dir}' "
                                 f"must be within the project directory '{project_dir}'")

        artifacts_path = self._get_artifacts_dir()
        if artifacts_path.exists():
            shutil.rmtree(artifacts_path)

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
        aggregated_result = event.aggregated_result
        for scenario_result in aggregated_result.scenario_results:
            scenario_artifacts_dir = self._get_scenario_artifacts_dir(scenario_result)
            self._ensure_exists(scenario_artifacts_dir)

            for step_result in scenario_result.step_results:
                for artifact in step_result.artifacts:
                    self._save_artifact(artifact, scenario_artifacts_dir)

            for artifact in scenario_result.artifacts:
                self._save_artifact(artifact, scenario_artifacts_dir)

    def _get_project_dir(self) -> Path:
        assert self._global_config is not None
        return self._global_config.project_dir

    def _get_artifacts_dir(self) -> Path:
        if self._artifacts_dir.is_absolute():
            return self._artifacts_dir
        return self._get_project_dir() / self._artifacts_dir

    def _get_scenario_artifacts_dir(self, scenario_result: ScenarioResult) -> Path:
        scenario = scenario_result.scenario
        scenario_path = self._get_artifacts_dir()
        scenario_path /= scenario.rel_path.with_suffix('')

        template_index = str(scenario.template_index or 0)
        started_at = str(scenario_result.started_at or 0).replace(".", "-")
        scenario_path /= f"{started_at}-{scenario.name}-{template_index}"

        return scenario_path

    def _ensure_exists(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)

    def _save_artifact(self, artifact: Artifact, scenario_path: Path) -> None:
        if isinstance(artifact, MemoryArtifact):
            artifact_path = scenario_path / artifact.name
            artifact_path.write_bytes(artifact.data)
        elif isinstance(artifact, FileArtifact):
            artifact_path = scenario_path / artifact.name
            shutil.copy2(artifact.path, artifact_path)
        else:
            artifact_type = type(artifact).__name__
            rel_path = scenario_path.relative_to(self._get_project_dir())
            raise TypeError(f"Can't save artifact to '{rel_path}:' unknown type '{artifact_type}'")


class Artifacted(PluginConfig):
    plugin = ArtifactedPlugin
    description = "Manages artifacts for step and scenario results"

    # Save artifacts to the file system
    save_artifacts: bool = False

    # Directory path for saving artifacts
    artifacts_dir: Path = Path(".vedro/artifacts/")
