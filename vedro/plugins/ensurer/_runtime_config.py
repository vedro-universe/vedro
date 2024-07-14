from typing import Union

from niltype import Nil, Nilable

from ._ensure import AttemptType, DelayType, LoggerType, SwallowExceptionType

__all__ = ("RuntimeConfig", "runtime_config",)


class RuntimeConfig:
    """
    Manages runtime configuration for attempts, delays, exception swallowing, and logging.

    This class allows setting and retrieving configuration parameters that control the behavior
    of retry mechanisms, including the number of attempts, delay between attempts,
    exceptions to swallow, and logging of attempts.
    """

    def __init__(self) -> None:
        """
        Initialize the RuntimeConfig instance with default Nil values.
        """
        self._attempts: Nilable[AttemptType] = Nil
        self._delay: Nilable[DelayType] = Nil
        self._swallow: Nilable[SwallowExceptionType] = Nil
        self._logger: Nilable[Union[LoggerType, None]] = Nil

    def get_attempts(self) -> AttemptType:
        """
        Retrieve the configured number of attempts.

        :return: The number of attempts.
        :raises ValueError: If attempts have not been set.
        """
        if self._attempts is Nil:
            raise ValueError("'attempts' is not set")
        return self._attempts

    def set_attempts(self, attempts: AttemptType) -> None:
        """
        Set the number of attempts.

        :param attempts: The number of attempts to set.
        """
        self._attempts = attempts

    def get_delay(self) -> DelayType:
        """
        Retrieve the configured delay.

        :return: The delay value or callable.
        :raises ValueError: If delay has not been set.
        """
        if self._delay is Nil:
            raise ValueError("'delay' is not set")
        return self._delay

    def set_delay(self, delay: DelayType) -> None:
        """
        Set the delay between attempts.

        :param delay: The delay value or callable to set.
        """
        self._delay = delay

    def get_swallow(self) -> SwallowExceptionType:
        """
        Retrieve the configured exceptions to swallow.

        :return: The exceptions to swallow.
        :raises ValueError: If swallow has not been set.
        """
        if self._swallow is Nil:
            raise ValueError("'swallow' is not set")
        return self._swallow

    def set_swallow(self, swallow: SwallowExceptionType) -> None:
        """
        Set the exceptions to swallow.

        :param swallow: The exceptions to swallow.
        """
        self._swallow = swallow

    def get_logger(self) -> Union[LoggerType, None]:
        """
        Retrieve the configured logger.

        :return: The logger.
        :raises ValueError: If logger has not been set.
        """
        if self._logger is Nil:
            raise ValueError("'logger' is not set")
        return self._logger

    def set_logger(self, logger: Union[LoggerType, None]) -> None:
        """
        Set the logger.

        :param logger: The logger to set.
        """
        self._logger = logger


runtime_config = RuntimeConfig()
