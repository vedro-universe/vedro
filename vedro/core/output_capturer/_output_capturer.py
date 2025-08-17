from typing import Any, Optional

from ._captured_output import CapturedOutput
from ._stream_buffer import StreamBuffer
from ._stream_view import StreamView

__all__ = ("OutputCapturer",)


class NoOpCapturedOutput(CapturedOutput):
    """
    Provides a no-op implementation of captured output.

    This class does not capture any output and is used when
    output capture is disabled.
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


class OutputCapturer:
    """
    Manages output capturing configuration and creates capture contexts.

    This class provides a clean interface for enabling or disabling output
    capture, and for applying a capture size limit.
    """

    def __init__(self, enabled: bool = False, capture_limit: Optional[int] = None) -> None:
        """
        Initialize an OutputCapturer.

        :param enabled: Whether output capturing is enabled.
        :param capture_limit: Maximum number of characters to capture.
                              If None, no limit is applied.
        """
        self._enabled = enabled
        self._capture_limit = capture_limit

    @property
    def enabled(self) -> bool:
        """
        Check whether output capturing is enabled.

        :return: True if capturing is enabled, False otherwise.
        """
        return self._enabled

    @property
    def capture_limit(self) -> Optional[int]:
        """
        Get the maximum capture size limit.

        :return: Maximum number of characters to capture, or None if unlimited.
        """
        return self._capture_limit

    def capture(self) -> CapturedOutput:
        """
        Create a context manager for capturing output.

        If capturing is enabled, returns a CapturedOutput instance.
        Otherwise, returns a NoOpCapturedOutput.

        :return: A CapturedOutput instance.
        """
        if self._enabled:
            return CapturedOutput(self._capture_limit)
        return NoOpCapturedOutput()
