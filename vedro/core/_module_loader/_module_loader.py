from abc import abstractmethod
from pathlib import Path
from types import ModuleType

__all__ = ("ModuleLoader",)


class ModuleLoader:
    @abstractmethod
    async def load(self, path: Path) -> ModuleType:
        raise NotImplementedError()
