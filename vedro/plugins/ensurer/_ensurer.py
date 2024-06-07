from typing import Optional, Type, Union

from vedro.core import Dispatcher, Plugin, PluginConfig
from vedro.events import StepFailedEvent, StepPassedEvent, StepRunEvent
from ._ensure import AttemptType, DelayType, Ensure, LoggerType, SwallowExceptionType
from ._runtime_config import RuntimeConfig
from ._runtime_config import runtime_config as _runtime_config

__all__ = ("Ensurer", "EnsurerPlugin", "ensure",)


def ensure(*, attempts: Optional[AttemptType] = None,
           delay: Optional[DelayType] = None,
           swallow: Optional[SwallowExceptionType] = None,
           logger: Optional[LoggerType] = None) -> Ensure:
    return Ensure(attempts=attempts or _runtime_config.get_attempts(),
                  delay=delay or _runtime_config.get_delay(),
                  swallow=swallow or _runtime_config.get_swallow(),
                  logger=logger or _runtime_config.get_logger())


class EnsurerPlugin(Plugin):
    def __init__(self, config: Type["Ensurer"], *,
                 runtime_config: RuntimeConfig = _runtime_config) -> None:
        super().__init__(config)
        self._runtime_config = runtime_config
        self._runtime_config.set_attempts(config.default_attempts)
        self._runtime_config.set_delay(config.default_delay)
        self._runtime_config.set_swallow(config.default_swallow)
        self._runtime_config.set_logger(None)

        self._show_attempts = config.show_attempts
        if self._show_attempts:
            self._runtime_config.set_logger(self._logger)
        self._last_log = []

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(StepRunEvent, self.on_step_run) \
                  .listen(StepPassedEvent, self.on_step_end) \
                  .listen(StepFailedEvent, self.on_step_end)

    def on_step_run(self, event: StepRunEvent) -> None:
        self._last_log = []

    def on_step_end(self, event: Union[StepPassedEvent, StepFailedEvent]) -> None:
        if not self._show_attempts:
            return

        if not self._last_log:
            return

        for fn, attempt, exc in self._last_log:
            orig_step = event.step_result.step._orig_step
            if fn != getattr(orig_step, "__wrapped__", orig_step):
                continue

            if exc:
                event.step_result.add_extra_details(f"[{attempt}] attempt failed with {exc!r}")
            else:
                event.step_result.add_extra_details(f"[{attempt}] attempt succeeded")

    def _logger(self, fn, attempt: int, exc: Union[BaseException, None]) -> None:
        self._last_log.append((fn, attempt, exc))


class Ensurer(PluginConfig):
    plugin = EnsurerPlugin
    description = "<description>"

    show_attempts = True

    default_attempts = 3

    default_delay = 0.0

    default_swallow = BaseException
