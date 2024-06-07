from niltype import Nil, Nilable

from ._ensure import AttemptType, DelayType, LoggerType, SwallowExceptionType

__all__ = ("RuntimeConfig", "runtime_config",)


class RuntimeConfig:
    def __init__(self) -> None:
        self._attempts: Nilable[AttemptType] = Nil
        self._delay: Nilable[DelayType] = Nil
        self._swallow: Nilable[SwallowExceptionType] = Nil
        self._logger: Nilable[LoggerType] = Nil

    def get_attempts(self) -> Nilable[AttemptType]:
        return self._attempts

    def set_attempts(self, attempts: AttemptType) -> None:
        self._attempts = attempts

    def get_delay(self) -> Nilable[DelayType]:
        return self._delay

    def set_delay(self, delay: DelayType) -> None:
        self._delay = delay

    def get_swallow(self) -> Nilable[SwallowExceptionType]:
        return self._swallow

    def set_swallow(self, swallow: SwallowExceptionType) -> None:
        self._swallow = swallow

    def get_logger(self) -> Nilable[LoggerType]:
        return self._logger

    def set_logger(self, logger: LoggerType) -> None:
        self._logger = logger


runtime_config = RuntimeConfig()
