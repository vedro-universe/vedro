import io
from typing import Optional

__all__ = ("StreamBuffer",)


class StreamBuffer(io.StringIO):
    """
    Stores captured output with optional size limiting.

    This class extends ``io.StringIO`` and enforces a maximum size constraint.
    When the captured content exceeds the size limit, older content is discarded.
    """

    def __init__(self, max_size: Optional[int] = None) -> None:
        """
        Initialize a StreamBuffer instance.

        :param max_size: Maximum number of characters to capture.
                         If None, no limit is applied.
        """
        super().__init__()
        self._max_size = max_size

    def write(self, s: str) -> int:
        """
        Write a string to the buffer with size limiting.

        If the buffer exceeds the maximum size, older content
        is trimmed to retain only the latest characters.

        :param s: String to write into the buffer.
        :return: Number of characters written.
        """
        result = super().write(s)

        if self._max_size is not None and self._max_size > 0:
            current_value = self.getvalue()
            if len(current_value) > self._max_size:
                trimmed = current_value[-self._max_size:]
                self.seek(0)
                self.truncate(0)
                super().write(trimmed)
                self.seek(0, io.SEEK_END)

        return result

    def get_value(self) -> str:
        """
        Retrieve the captured buffer content.

        :return: The captured output as a string.
        """
        return self.getvalue()
