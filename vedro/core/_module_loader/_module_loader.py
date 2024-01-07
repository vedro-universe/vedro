from abc import ABC, abstractmethod
from pathlib import Path
from types import ModuleType

__all__ = ("ModuleLoader",)


class ModuleLoader(ABC):
    """
    Abstract base class for a module loader.

    This class defines an interface for loading Python modules.
    """

    @abstractmethod
    async def load(self, path: Path) -> ModuleType:
        """
        Load a module from a given path.

        :param path: The file path of the module to be loaded.
        """
        pass
