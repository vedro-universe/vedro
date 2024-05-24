from abc import ABC, abstractmethod
from pathlib import Path
from types import ModuleType

__all__ = ("ModuleLoader",)


class ModuleLoader(ABC):
    """
    Represents an abstract base class for module loading.

    This class defines the interface for loading a module from a given file path.
    Subclasses must implement the `load` method to provide the specific module loading
    functionality.
    """

    @abstractmethod
    async def load(self, path: Path) -> ModuleType:
        """
        Load a module from the specified file path.

        :param path: The file path to load the module from.
        :return: The loaded module.
        :raises NotImplementedError: If the method is not implemented by a subclass.
        """
        pass
