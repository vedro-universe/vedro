from ._stream_buffer import StreamBuffer

__all__ = ("StreamView",)


class StreamView:
    """
    A read-only view of a StreamBuffer.

    Provides read-only access to the captured output.
    """

    def __init__(self, buffer: StreamBuffer) -> None:
        """
        Initialize a StreamView.

        :param buffer: The underlying StreamBuffer to wrap.
        """
        self._buffer = buffer

    def get_value(self) -> str:
        """
        Get the captured output value.

        :return: The captured string content.
        """
        return self._buffer.get_value()
