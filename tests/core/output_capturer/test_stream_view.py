from baby_steps import given, then, when

from vedro.core.output_capturer import StreamBuffer, StreamView


def test_stream_view_get_value():
    with given:
        buffer = StreamBuffer()
        test_content = "Hello, World!"
        buffer.write(test_content)

    with when:
        view = StreamView(buffer)
        result = view.get_value()

    with then:
        assert result == test_content


def test_stream_view_empty_buffer():
    with given:
        buffer = StreamBuffer()
        view = StreamView(buffer)

    with when:
        result = view.get_value()

    with then:
        assert result == ""
