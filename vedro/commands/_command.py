from abc import ABC, abstractmethod
from typing import Any, Type

from vedro import Config

from ._cmd_arg_parser import CommandArgumentParser

__all__ = ("Command",)


class Command(ABC):
    """
    Serves as an abstract base class for defining commands.

    Commands are operations that can be executed with a specific configuration
    and argument parser. Subclasses must implement the `run` method to define
    the behavior of the command.

    :param config: The global configuration instance for the command.
    :param arg_parser: The argument parser for parsing command-line options.
    :param kwargs: Additional keyword arguments for customization.
    """

    def __init__(self, config: Type[Config],
                 arg_parser: CommandArgumentParser, **kwargs: Any) -> None:
        """
        Initialize the Command instance with a configuration and argument parser.

        :param config: The global configuration instance.
        :param arg_parser: The argument parser for parsing command-line options.
        :param kwargs: Additional keyword arguments for customization.
        """
        self._config = config
        self._arg_parser = arg_parser

    @abstractmethod
    async def run(self) -> None:
        """
        Execute the command's logic.

        Subclasses must implement this method to define the specific behavior
        of the command when executed.
        """
        pass
