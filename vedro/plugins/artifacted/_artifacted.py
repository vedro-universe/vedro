import shutil
from collections import deque
from pathlib import Path
from typing import Deque, Type, Union, final

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
    CleanupEvent,
    ConfigLoadedEvent,
    ScenarioFailedEvent,
    ScenarioPassedEvent,
    ScenarioReportedEvent,
    ScenarioRunEvent,
    StepFailedEvent,
    StepPassedEvent,
)

from ._utils import is_relative_to

__all__ = ("Artifacted", "ArtifactedPlugin", "attach_artifact", "attach_step_artifact",
           "attach_scenario_artifact", "attach_global_artifact")


_scenario_artifacts: Deque[Artifact] = deque()
_step_artifacts: Deque[Artifact] = deque()
_global_artifacts: Deque[Artifact] = deque()


def attach_scenario_artifact(artifact: Artifact) -> None:
    """
    Attach an artifact to the current scenario.

    :param artifact: The artifact to be attached to the scenario.
    """
    _scenario_artifacts.append(artifact)


def attach_step_artifact(artifact: Artifact) -> None:
    """
    Attach an artifact to the current step.

    :param artifact: The artifact to be attached to the step.
    """
    _step_artifacts.append(artifact)


def attach_artifact(artifact: Artifact) -> None:
    """
    Attach an artifact to the current step. Alias for attach_step_artifact().

    :param artifact: The artifact to be attached.
    """
    attach_step_artifact(artifact)


def attach_global_artifact(artifact: Artifact) -> None:
    """
    Attach an artifact to the entire test run.

    :param artifact: The artifact to be attached globally.
    """
    _global_artifacts.append(artifact)


@final
class ArtifactedPlugin(Plugin):
    """
    Manages artifacts for steps and scenarios during the test execution.

    This plugin handles artifact collection and saving, ensuring artifacts are attached
    to the appropriate step or scenario, and optionally saved to the file system.
    """

    def __init__(self, config: Type["Artifacted"], *,
                 global_artifacts: Deque[Artifact] = _global_artifacts,
                 scenario_artifacts: Deque[Artifact] = _scenario_artifacts,
                 step_artifacts: Deque[Artifact] = _step_artifacts) -> None:
        """
        Initialize the ArtifactedPlugin with the provided configuration.

        :param config: The Artifacted configuration class.
        :param scenario_artifacts: The deque holding scenario artifacts.
        :param step_artifacts: The deque holding step artifacts.
        :param global_artifacts: The deque holding global artifacts.
        """
        super().__init__(config)
        self._global_artifacts = global_artifacts
        self._scenario_artifacts = scenario_artifacts
        self._step_artifacts = step_artifacts
        self._save_artifacts = config.save_artifacts
        self._artifacts_dir = config.artifacts_dir
        self._add_artifact_details = config.add_artifact_details
        self._cleanup_artifacts_dir = config.cleanup_artifacts_dir
        self._global_config: Union[ConfigType, None] = None

    def subscribe(self, dispatcher: Dispatcher) -> None:
        """
        Subscribe to the necessary Vedro events for managing artifacts.

        :param dispatcher: The event dispatcher to register listeners on.
        """
        dispatcher.listen(ConfigLoadedEvent, self.on_config_loaded) \
                  .listen(ArgParseEvent, self.on_arg_parse) \
                  .listen(ArgParsedEvent, self.on_arg_parsed) \
                  .listen(ScenarioRunEvent, self.on_scenario_run) \
                  .listen(StepPassedEvent, self.on_step_end) \
                  .listen(StepFailedEvent, self.on_step_end) \
                  .listen(ScenarioPassedEvent, self.on_scenario_end) \
                  .listen(ScenarioFailedEvent, self.on_scenario_end) \
                  .listen(ScenarioReportedEvent, self.on_scenario_reported) \
                  .listen(CleanupEvent, self.on_cleanup)

    def on_config_loaded(self, event: ConfigLoadedEvent) -> None:
        """
        Handle the event when the configuration is loaded.

        :param event: The ConfigLoadedEvent instance containing the configuration.
        """
        self._global_config = event.config

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        """
        Handle the event when arguments are being parsed, adding artifact-related arguments.

        :param event: The ArgParseEvent instance for parsing arguments.
        """
        group = event.arg_parser.add_argument_group("Artifacted")

        save_artifacts_group = group.add_mutually_exclusive_group()
        save_artifacts_group.add_argument("--save-artifacts",
                                          action="store_true",
                                          default=self._save_artifacts,
                                          help="Save artifacts to the file system")
        save_artifacts_group.add_argument("--no-save-artifacts",
                                          dest="save_artifacts",
                                          action="store_false",
                                          help="Disable saving artifacts to the file system")

        group.add_argument("--artifacts-dir", type=Path, default=None,
                           help=("Specify the directory path for saving artifacts "
                                 f"(default: '{self._artifacts_dir}')"))

        add_details_group = group.add_mutually_exclusive_group()
        add_details_group.add_argument("--add-artifact-details", action="store_true",
                                       default=self._add_artifact_details,
                                       help="Add artifact details to scenario and step extras")
        add_details_group.add_argument("--no-add-artifact-details", action="store_false",
                                       dest="add_artifact_details",
                                       help=("Disable adding artifact details to scenario and "
                                             "step extras"))

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        """
        Handle the event after arguments have been parsed, processing artifact options.

        :param event: The ArgParsedEvent instance containing parsed arguments.
        :raises ValueError: If artifacts directory is specified but saving is disabled.
        """
        self._global_artifacts.clear()

        self._add_artifact_details = event.args.add_artifact_details
        self._save_artifacts = event.args.save_artifacts
        if not self._save_artifacts:
            if event.args.artifacts_dir is not None:
                raise ValueError(
                    "Artifacts directory cannot be specified when artifact saving is disabled")
            if self._add_artifact_details:
                raise ValueError(
                    "Adding artifact details requires artifact saving to be enabled")
            return

        self._artifacts_dir = event.args.artifacts_dir or self._artifacts_dir

        project_dir = self._get_project_dir()
        if not self._artifacts_dir.is_absolute():
            self._artifacts_dir = (project_dir / self._artifacts_dir).resolve()
        if not is_relative_to(self._artifacts_dir, project_dir):
            raise ValueError(f"Artifacts directory '{self._artifacts_dir}' "
                             f"must be within the project directory '{project_dir}'")

        if self._cleanup_artifacts_dir and self._artifacts_dir.exists():
            shutil.rmtree(self._artifacts_dir)

    def on_scenario_run(self, event: ScenarioRunEvent) -> None:
        """
        Handle the event when a scenario run starts, clearing artifact deques.

        :param event: The ScenarioRunEvent instance.
        """
        self._scenario_artifacts.clear()
        self._step_artifacts.clear()

    async def on_step_end(self, event: Union[StepPassedEvent, StepFailedEvent]) -> None:
        """
        Handle the event when a step ends, attaching artifacts to the step result.

        :param event: The StepPassedEvent or StepFailedEvent instance.
        """
        while len(self._step_artifacts) > 0:
            artifact = self._step_artifacts.popleft()
            event.step_result.attach(artifact)

    async def on_scenario_end(self,
                              event: Union[ScenarioPassedEvent, ScenarioFailedEvent]) -> None:
        """
        Handle the event when a scenario ends, attaching artifacts to the scenario result.

        :param event: The ScenarioPassedEvent or ScenarioFailedEvent instance.
        """
        while len(self._scenario_artifacts) > 0:
            artifact = self._scenario_artifacts.popleft()
            event.scenario_result.attach(artifact)

    async def on_scenario_reported(self, event: ScenarioReportedEvent) -> None:
        """
        Handle the event after a scenario has been reported, saving artifacts if configured.

        :param event: The ScenarioReportedEvent instance.
        """
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

    async def on_cleanup(self, event: CleanupEvent) -> None:
        if not self._save_artifacts:
            return

        artifacts = []

        global_artifacts_dir = self._artifacts_dir / "global"
        for artifact in self._global_artifacts:
            artifact_path = self._save_artifact(artifact, global_artifacts_dir)
            artifacts.append(artifact_path.relative_to(self._get_project_dir()))

        if self._add_artifact_details and len(artifacts) > 0:
            summary = "global artifacts:\n#   - " + "\n#   - ".join(str(x) for x in artifacts)
            event.report.add_summary(summary)

    def _add_extra_details(self, result: Union[ScenarioResult, StepResult],
                           artifact_path: Path) -> None:
        """
        Add artifact details to the scenario or step result, if configured.

        :param result: The ScenarioResult or StepResult to attach extra details to.
        :param artifact_path: The file path where the artifact was saved.
        """
        if self._add_artifact_details:
            rel_path = artifact_path.relative_to(self._get_project_dir())
            result.add_extra_details(f"artifact '{rel_path}'")

    def _get_project_dir(self) -> Path:
        """
        Get the project's root directory.

        :return: The resolved Path to the project directory.
        """
        assert self._global_config is not None  # for type checker
        return self._global_config.project_dir.resolve()

    def _get_scenario_artifacts_dir(self, scenario_result: ScenarioResult) -> Path:
        """
        Get the directory path where artifacts for a scenario should be stored.

        :param scenario_result: The ScenarioResult instance.
        :return: The Path to the directory for the scenario's artifacts.
        """
        scenario = scenario_result.scenario
        scenario_path = self._artifacts_dir / scenario.rel_path.with_suffix('')

        template_index = str(scenario.template_index or 0)
        started_at = str(scenario_result.started_at or 0).replace(".", "-")
        scenario_path /= f"{started_at}-{scenario.name}-{template_index}"

        return scenario_path

    def _save_artifact(self, artifact: Artifact, path: Path) -> Path:
        """
        Save an artifact to the file system.

        :param artifact: The artifact to be saved.
        :param path: The directory path where the artifact should be saved.
        :return: The Path to the saved artifact.
        :raises TypeError: If the artifact type is unknown.
        """
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

        if isinstance(artifact, MemoryArtifact):
            artifact_dest_path = (path / artifact.name).resolve()
            artifact_dest_path.write_bytes(artifact.data)
            return artifact_dest_path

        elif isinstance(artifact, FileArtifact):
            artifact_dest_path = (path / artifact.name).resolve()
            artifact_source_path = artifact.path
            if not artifact_source_path.is_absolute():
                artifact_source_path = (self._get_project_dir() / artifact_source_path).resolve()
            shutil.copy2(artifact_source_path, artifact_dest_path)
            return artifact_dest_path

        else:
            artifact_type = type(artifact).__name__
            rel_path = path.relative_to(self._get_project_dir())
            raise TypeError(f"Can't save artifact to '{rel_path}': unknown type '{artifact_type}'")


class Artifacted(PluginConfig):
    """
    Configuration class for the ArtifactedPlugin.

    Defines default settings for managing artifacts during test steps and scenarios, including
    saving them to the file system and attaching extra details to test results.
    """

    plugin = ArtifactedPlugin
    description = "Manages artifacts for step and scenario results"

    # Enable or disable saving artifacts to the file system.
    # If False, artifacts will not be saved, and `artifacts_dir` cannot be specified.
    save_artifacts: bool = True

    # Directory path where artifacts will be saved.
    # This option is only applicable if `save_artifacts` is set to True.
    # If unspecified, the default directory is ".vedro/artifacts/".
    artifacts_dir: Path = Path(".vedro/artifacts/")

    # Enable or disable adding artifact details to scenario and step extras.
    # This option is only applicable if `save_artifacts` is set to True.
    # If `save_artifacts` is False and this is True, a ValueError will be raised.
    add_artifact_details: bool = True

    # Enable or disable cleanup of the artifacts directory before starting the test run.
    # If True, the artifacts directory will be removed at the start of the test run.
    cleanup_artifacts_dir: bool = True
