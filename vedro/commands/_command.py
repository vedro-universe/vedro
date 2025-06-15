from abc import ABC, abstractmethod
from typing import Any, Type

from vedro import Config

from ._cmd_arg_parser import CommandArgumentParser

__all__ = ("Command",)


class Command(ABC):
    """
    Serves as an abstract base class for defining commands.

    Commands are operations that can be executed with a specific configuration
    and argument parser. Subclasses of `Command` must implement the `run` method
    to define the behavior of the command. These commands are typically invoked
    as part of a CLI or other runtime interface.
    """

    def __init__(self, config: Type[Config],
                 arg_parser: CommandArgumentParser, **kwargs: Any) -> None:
        """
        Initialize the Command instance with a configuration and argument parser.

        :param config: The global configuration instance used by the command.
        :param arg_parser: The argument parser for parsing command-line options.
        :param kwargs: Additional keyword arguments for customization, if needed.
        """
        self._config = config
        self._arg_parser = arg_parser

    @abstractmethod
    async def run(self) -> None:
        """
        Execute the command's logic.

        Subclasses must override this method to define the specific behavior
        of the command. This method should contain the main execution flow
        of the command.

        :raises NotImplementedError: If the subclass does not implement this method.
        """
        pass
