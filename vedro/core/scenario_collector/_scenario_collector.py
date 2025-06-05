from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from vedro.core import VirtualScenario

__all__ = ("ScenarioCollector",)


class ScenarioCollector(ABC):
    @abstractmethod
    async def collect(self, path: Path, *, project_dir: Path) -> List[VirtualScenario]:
        pass
