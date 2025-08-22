from typing import Optional

from ._captured_output import CapturedOutput, NoOpCapturedOutput

__all__ = ("OutputCapturer",)


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
        Otherwise, returns a NoCapturedOutput.

        :return: A CapturedOutput instance.
        """
        if self._enabled:
            return CapturedOutput(self._capture_limit)
        return NoOpCapturedOutput()
