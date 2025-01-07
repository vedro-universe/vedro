from abc import ABC, abstractmethod
from pathlib import Path
from typing import AsyncGenerator

__all__ = ("ScenarioFinder",)


class ScenarioFinder(ABC):
    """
    Abstract base class for a scenario finder.

    This class defines the interface for finding scenario files in a specified location.
    Concrete implementations of this class should provide the functionality to
    traverse a given path and yield the paths of scenario files that meet certain criteria.
    """

    @abstractmethod
    async def find(self, root: Path) -> AsyncGenerator[Path, None]:
        """
        Find and yield paths to scenario files starting from the given root directory.

        This is an abstract method that must be implemented by subclasses. It should define
        how scenario files are located and yielded from the specified root directory.

        :param root: The root directory path to start the search for scenario files.
        :yield: Paths to scenario files found under the root directory.
        :raises NotImplementedError: If the method is not implemented in a subclass.
        """
        # Placeholder due to https://github.com/python/mypy/issues/5070
        yield Path()
