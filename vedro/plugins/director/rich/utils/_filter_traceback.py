from pathlib import Path
from types import ModuleType, TracebackType
from typing import Sequence, Union

__all__ = ("TracebackFilter",)


class TracebackFilter:
    """
    Filters traceback objects to exclude frames from specified modules.

    This class provides methods to filter out frames from traceback objects
    that belong to specified modules, making it easier to focus on relevant
    parts of the traceback.
    """

    def __init__(self, modules: Sequence[Union[str, ModuleType]]) -> None:
        """
        Initialize the TracebackFilter with a list of modules to filter out.

        :param modules: List of modules or module paths to be filtered out from tracebacks.
        """
        self._module_paths = [self.resolve_module_path(m) for m in modules]

    def filter_tb(self, tb: TracebackType) -> TracebackType:
        """
        Filter the given traceback, removing frames from specified modules.

        :param tb: The original traceback object to be filtered.
        :return: A new traceback object with frames from the specified modules removed.
        """
        filtered_tb = None
        last_tb = None

        while tb is not None:
            filename = Path(tb.tb_frame.f_code.co_filename)

            if not any(self._is_relative_to(filename, m) for m in self._module_paths):
                # Create a new traceback object if it is not a filtered file
                if last_tb is None:
                    # Create a new 'root' traceback
                    filtered_tb = tb
                    last_tb = tb
                else:
                    # Append the current traceback to the last valid traceback
                    last_tb.tb_next = tb
                    last_tb = tb

            # Move to the next traceback object
            tb = tb.tb_next  # type: ignore

        # Ensure the last traceback in the chain doesn't link to excluded frames
        if last_tb is not None:
            last_tb.tb_next = None

        return filtered_tb

    def resolve_module_path(self, module: Union[str, ModuleType]) -> Path:
        """
        Resolve the module path from a module or string.

        :param module: A module object or module path as a string.
        :return: The resolved Path object of the module.
        :raises AttributeError: If the module object does not have a '__file__' attribute.
        :raises TypeError: If the module is neither a string nor a module object.
        """
        if isinstance(module, ModuleType):
            if module_path := getattr(module, "__file__", None):
                return Path(module_path).parent
            raise AttributeError(
                f"'{module.__name__}' must be a module with a '__file__' attribute")

        if isinstance(module, str):
            return Path(module).resolve()

        raise TypeError(f"'{module}' must be a module or a path")

    def _is_relative_to(self, path: Path, other: Path) -> bool:
        """
        Check if the path is relative to another path.

        (Path.is_relative_to() is available since Python 3.9)

        :param path: The path to be checked.
        :param other: The reference path.
        :return: True if 'path' is relative to 'other', False otherwise.
        """
        try:
            path.relative_to(other)
        except ValueError:
            return False
        return True
