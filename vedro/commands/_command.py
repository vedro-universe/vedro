from abc import ABC, abstractmethod
from typing import Any, Type

from vedro import Config

from ._cmd_arg_parser import CommandArgumentParser

__all__ = ("Command",)


class Command(ABC):
    def __init__(self, config: Type[Config],
                 arg_parser: CommandArgumentParser, **kwargs: Any) -> None:
        self._config = config
        self._arg_parser = arg_parser

    @abstractmethod
    async def run(self) -> None:
        pass
