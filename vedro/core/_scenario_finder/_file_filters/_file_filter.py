from abc import ABC, abstractmethod
from pathlib import Path

__all__ = ("FileFilter",)


class FileFilter(ABC):
    @abstractmethod
    def filter(self, path: Path) -> bool:
        pass
