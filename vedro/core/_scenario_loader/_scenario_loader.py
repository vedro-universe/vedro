from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Type

from ..._scenario import Scenario

__all__ = ("ScenarioLoader",)


class ScenarioLoader(ABC):
    @abstractmethod
    async def load(self, path: Path) -> List[Type[Scenario]]:
        pass
