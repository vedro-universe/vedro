from abc import ABC, abstractmethod
from pathlib import Path
from typing import AsyncGenerator

__all__ = ("ScenarioFinder",)


class ScenarioFinder(ABC):
    @abstractmethod
    async def find(self, root: Path) -> AsyncGenerator[Path, None]:
        # https://github.com/python/mypy/issues/5070
        yield Path()
