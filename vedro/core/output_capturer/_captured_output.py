from contextlib import redirect_stderr, redirect_stdout
from typing import Any, Optional, TextIO

from ._stream_buffer import StreamBuffer
from ._stream_view import StreamView

__all__ = ("CapturedOutput", "NoOpCapturedOutput",)


class CapturedOutput:
    """
    Captures both stdout and stderr output into a buffer.

    This context manager redirects both stdout and stderr streams
    into a single buffer, preserving interleaved order.
    """

    def __init__(self, capture_limit: Optional[int] = None) -> None:
        """
        Initialize a CapturedOutput context manager.

        :param capture_limit: Maximum number of characters to capture per stream
                              (stdout and stderr are limited independently).
                              If None, no limit is applied.
        """
        self._stdout_buffer = StreamBuffer(capture_limit)
        self._stderr_buffer = StreamBuffer(capture_limit)
        # TODO: Consider using SpooledTemporaryFile instead of StreamBuffer for larger outputs
        # that would benefit from disk-based storage rather than in-memory only
        self._stdout_context: Optional[redirect_stdout[TextIO]] = None
        self._stderr_context: Optional[redirect_stderr[TextIO]] = None

    @property
    def stdout(self) -> StreamView:
        """
        Get a read-only view of the captured stdout.

        :return: A StreamView instance for stdout.
        """
        return StreamView(self._stdout_buffer)

    @property
    def stderr(self) -> StreamView:
        """
        Get a read-only view of the captured stderr.

        :return: A StreamView instance for stderr.
        """
        return StreamView(self._stderr_buffer)

    def __enter__(self) -> "CapturedOutput":
        """
        Enter the context manager and start capturing stdout and stderr.

        :return: The CapturedOutput instance.
        """
        self._stdout_context = redirect_stdout(self._stdout_buffer)
        self._stderr_context = redirect_stderr(self._stderr_buffer)
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
        if self._stdout_context:  # pragma: no branch
            self._stdout_context.__exit__(exc_type, exc_val, exc_tb)
        if self._stderr_context:  # pragma: no branch
            self._stderr_context.__exit__(exc_type, exc_val, exc_tb)


class NoOpCapturedOutput(CapturedOutput):
    """
    No-operation implementation of CapturedOutput that doesn't capture any output.

    This class is used when output capture is disabled, providing
    the same interface without performing any actual capture operations.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize a NoOpCapturedOutput with an empty buffer.

        :param args: Positional arguments (ignored).
        :param kwargs: Keyword arguments (ignored).
        """
        # Don't call super().__init__ to avoid creating buffers
        self._stream_view = StreamView(StreamBuffer())

    @property
    def stdout(self) -> StreamView:
        """
        Get a stream view for stdout that always returns empty content.

        :return: A StreamView instance with an empty buffer.
        """
        return self._stream_view

    @property
    def stderr(self) -> StreamView:
        """
        Get a stream view for stderr that always returns empty content.

        :return: A StreamView instance with an empty buffer.
        """
        return self._stream_view

    def __enter__(self) -> "NoOpCapturedOutput":
        """
        Enter the no-op context.

        :return: The NoOpCapturedOutput instance.
        """
        return self

    def __exit__(self, exc_type: Optional[type], exc_val: Optional[Exception],
                 exc_tb: Optional[Any]) -> None:
        """
        Exit the no-op context. Does nothing.

        :param exc_type: Exception type if raised inside the context.
        :param exc_val: Exception instance if raised inside the context.
        :param exc_tb: Traceback object if raised inside the context.
        """
        pass
