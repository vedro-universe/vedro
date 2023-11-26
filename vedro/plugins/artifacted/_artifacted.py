import shutil
from collections import deque
from pathlib import Path
from typing import Deque, Type, Union

from vedro.core import (
    Artifact,
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
        self._artifacts_dir = ".vedro/artifacts"

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ArgParseEvent, self.on_arg_parse) \
                  .listen(ArgParsedEvent, self.on_arg_parsed) \
                  .listen(ScenarioRunEvent, self.on_scenario_run) \
                  .listen(StepPassedEvent, self.on_step_end) \
                  .listen(StepFailedEvent, self.on_step_end) \
                  .listen(ScenarioPassedEvent, self.on_scenario_end) \
                  .listen(ScenarioFailedEvent, self.on_scenario_end) \
                  .listen(ScenarioReportedEvent, self.on_scenario_reported)

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        event.arg_parser.add_argument("--save-artifacts", action="store_true",
                                      default=self._save_artifacts, help="<message>")

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        self._save_artifacts = event.args.save_artifacts

        artifacts_path = self._get_artifacts_path()
        if artifacts_path.exists():
            shutil.rmtree(artifacts_path, ignore_errors=True)

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

    def _get_artifacts_path(self) -> Path:
        return Path.cwd() / self._artifacts_dir

    def _get_scenario_path(self, scenario_result: ScenarioResult) -> Path:
        scenario = scenario_result.scenario
        scenario_path = self._get_artifacts_path()
        scenario_path /= scenario.rel_path.with_suffix('')

        template_index = str(scenario.template_index or 0)
        started_at = str(scenario_result.started_at or 0).replace(".", "-")
        scenario_path /= f"{started_at}-{scenario.name}-{template_index}"

        return scenario_path

    def _save_artifact(self, artifact: Artifact, scenario_path: Path) -> None:
        scenario_path.mkdir(parents=True, exist_ok=True)

        if isinstance(artifact, MemoryArtifact):
            artifact_path = scenario_path / artifact.name
            artifact_path.write_bytes(artifact.data)
        elif isinstance(artifact, FileArtifact):
            artifact_path = scenario_path / artifact.name
            shutil.copy2(artifact.path, artifact_path)
        else:
            raise Exception("Unknown artifact type")

    async def on_scenario_reported(self, event: ScenarioReportedEvent) -> None:
        aggregated_result = event.aggregated_result
        for scenario_result in aggregated_result.scenario_results:
            for step_result in scenario_result.step_results:
                for artifact in step_result.artifacts:
                    self._save_artifact(artifact, self._get_scenario_path(scenario_result))
            for artifact in scenario_result.artifacts:
                self._save_artifact(artifact, self._get_scenario_path(scenario_result))


class Artifacted(PluginConfig):
    plugin = ArtifactedPlugin
    description = "Manages artifacts for step and scenario results"

    save_artifacts: bool = False
