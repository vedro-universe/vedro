from collections import deque
from typing import Deque, Type, Union

from vedro.core import Artifact, Dispatcher, Plugin, PluginConfig
from vedro.events import (
    ScenarioFailedEvent,
    ScenarioPassedEvent,
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

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ScenarioRunEvent, self.on_scenario_run) \
                  .listen(StepPassedEvent, self.on_step_end) \
                  .listen(StepFailedEvent, self.on_step_end) \
                  .listen(ScenarioPassedEvent, self.on_scenario_end) \
                  .listen(ScenarioFailedEvent, self.on_scenario_end)

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


class Artifacted(PluginConfig):
    plugin = ArtifactedPlugin
