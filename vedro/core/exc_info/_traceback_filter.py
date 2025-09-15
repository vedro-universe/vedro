from pathlib import Path
from types import FrameType, ModuleType, TracebackType
from typing import Callable, Sequence, Union

__all__ = ("TracebackFilter", "NoOpTracebackFilter", "TracebackFilterType",)


# NOTE FOR PLUGIN DEVELOPERS:
# Do not instantiate TracebackFilter directly. Always use Config.Registry.TracebackFilter instead.
# The registry may replace the default filter (for example, with a no-op filter in debug mode),
# so using it ensures all plugins respect the global configuration and behave consistently.
#
# Example:
# class CustomPlugin(Plugin):
#     def on_config_loaded(self, event: ConfigLoadedEvent) -> None:
#         self._global_config = event.config
#
#     def on_arg_parsed(self, event: ArgParsedEvent) -> None:
#         tb_filter_factory = self._global_config.Registry.TracebackFilter
#         tb_filter = tb_filter_factory(modules=[...])
class TracebackFilter:
    """
    Filters traceback objects to exclude frames from specified modules
    and frames marked with __tracebackhide__ or __traceback_hide__.

    This class provides methods to filter out frames from traceback objects
    that belong to specified modules or are marked for hiding, making it
    easier to focus on relevant parts of the traceback.
    """

    def __init__(self, modules: Sequence[Union[str, ModuleType]], *,
                 skip_hidden_frames: bool = True) -> None:
        """
        Initialize the TracebackFilter with a list of modules to filter out.

        :param modules: List of modules or module paths to be filtered out from tracebacks.
        :param skip_hidden_frames: Whether to skip frames marked with __tracebackhide__ or
                                   __traceback_hide__.
        """
        self._module_paths = [self.resolve_module_path(m) for m in modules]
        self._skip_hidden_frames = skip_hidden_frames

    def filter_tb(self, tb: TracebackType) -> TracebackType:
        """
        Filter the given traceback, removing frames from specified modules
        and frames marked with __tracebackhide__ or __traceback_hide__.

        :param tb: The original traceback object to be filtered.
        :return: A new traceback object with hidden frames removed.
        """
        filtered_tb = None
        last_tb = None

        while tb is not None:
            if not self.should_hide_frame(tb.tb_frame):
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

    def should_hide_frame(self, frame: FrameType) -> bool:
        """
        Determine if a frame should be hidden based on module paths and hide flags.

        :param frame: The frame object to check.
        :return: True if the frame should be hidden, False otherwise.
        """
        filename = Path(frame.f_code.co_filename)
        if any(self._is_relative_to(filename, m) for m in self._module_paths):
            return True

        if not self._skip_hidden_frames:
            return False

        for flag in ("__traceback_hide__", "__tracebackhide__"):
            if frame.f_locals.get(flag, False):
                return True

        return False

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


class NoOpTracebackFilter(TracebackFilter):
    """
    No-operation implementation of TracebackFilter that preserves all frames.

    This implementation returns tracebacks unchanged, useful for debug mode
    or when complete stack traces are needed without any filtering.
    """

    def filter_tb(self, tb: TracebackType) -> TracebackType:
        """
        Return the traceback unfiltered.

        :param tb: The original traceback object.
        :return: The same traceback object without any filtering.
        """
        return tb


TracebackFilterType = Union[
    TracebackFilter,
    Callable[[Sequence[Union[str, ModuleType]]], TracebackFilter]
]
