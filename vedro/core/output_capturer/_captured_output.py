from contextlib import redirect_stderr, redirect_stdout
from typing import Any, Optional, TextIO

from ._stream_buffer import StreamBuffer

__all__ = ("CapturedOutput",)


class CapturedOutput:
    """
    Captures both stdout and stderr output into a buffer.

    This context manager redirects both stdout and stderr streams
    into a single buffer, preserving interleaved order.
    """

    def __init__(self, capture_limit: Optional[int] = None) -> None:
        """
        Initialize a CapturedOutput context manager.

        :param capture_limit: Maximum number of characters to capture.
                              If None, no limit is applied.
        """
        self._buffer = StreamBuffer(capture_limit)
        # TODO: Consider using SpooledTemporaryFile instead of StreamBuffer for larger outputs
        # that would benefit from disk-based storage rather than in-memory only
        self._stdout_context: Optional[redirect_stdout[TextIO]] = None
        self._stderr_context: Optional[redirect_stderr[TextIO]] = None

    def get_value(self) -> str:
        """
        Get the captured output from the buffer.

        :return: The captured output as a string.
        """
        return self._buffer.get_value()

    def __enter__(self) -> "CapturedOutput":
        """
        Enter the context manager and start capturing stdout and stderr.

        :return: The CapturedOutput instance.
        """
        self._stdout_context = redirect_stdout(self._buffer)
        self._stderr_context = redirect_stderr(self._buffer)
        self._stdout_context.__enter__()
        self._stderr_context.__enter__()
        return self

    def __exit__(self, exc_type: Optional[type], exc_val: Optional[Exception],
                 exc_tb: Optional[Any]) -> None:
        """
        Exit the context manager and stop capturing output.

        :param exc_type: Exception type if raised inside the context.
        :param exc_val: Exception instance if raised inside the context.
        :param exc_tb: Traceback object if raised inside the context.
        """
        if self._stdout_context:
            self._stdout_context.__exit__(exc_type, exc_val, exc_tb)
        if self._stderr_context:
            self._stderr_context.__exit__(exc_type, exc_val, exc_tb)
