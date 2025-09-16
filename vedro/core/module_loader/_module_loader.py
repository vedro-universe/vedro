from abc import ABC, abstractmethod
from pathlib import Path
from types import ModuleType

__all__ = ("ModuleLoader",)


# TODO (v2): Consider separating concerns:
#  - Rename this class to ScenarioLoader (async, for test discovery/loading)
#  - Create a new sync ModuleLoader for general module operations
#  This would clarify that scenarios have different loading requirements
#  than general Python modules
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
