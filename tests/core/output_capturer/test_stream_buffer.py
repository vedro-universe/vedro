from baby_steps import given, then, when

from vedro.core.output_capturer import StreamBuffer


def test_stream_buffer_initialization():
    with when:
        buffer = StreamBuffer()

    with then:
        assert buffer.get_value() == ""
        assert buffer.max_size is None


def test_stream_buffer_initialization_with_max_size():
    with given:
        max_size = 100

    with when:
        buffer = StreamBuffer(max_size)

    with then:
        assert buffer.get_value() == ""
        assert buffer.max_size == max_size


def test_stream_buffer_write_single_string():
    with given:
        buffer = StreamBuffer()
        text = "Hello, World!"

    with when:
        result = buffer.write(text)

    with then:
        assert result == len(text)
        assert buffer.get_value() == text


def test_stream_buffer_write_multiple_strings():
    with given:
        buffer = StreamBuffer()
        text1 = "First line\n"
        text2 = "Second line\n"
        text3 = "Third line"

        buffer.write(text1)
        buffer.write(text2)

    with when:
        buffer.write(text3)

    with then:
        expected = text1 + text2 + text3
        assert buffer.get_value() == expected


def test_stream_buffer_write_empty_string():
    with given:
        buffer = StreamBuffer()
        initial_text = "Initial content"
        buffer.write(initial_text)

    with when:
        result = buffer.write("")

    with then:
        assert result == 0
        assert buffer.get_value() == initial_text


def test_stream_buffer_with_max_size_under_limit():
    with given:
        max_size = 20
        buffer = StreamBuffer(max_size)
        text = "Short text"

    with when:
        buffer.write(text)

    with then:
        assert buffer.get_value() == text


def test_stream_buffer_with_max_size_at_limit():
    with given:
        max_size = 10
        buffer = StreamBuffer(max_size)
        text = "1234567890"  # Exactly 10 characters

    with when:
        buffer.write(text)

    with then:
        assert buffer.get_value() == text


def test_stream_buffer_with_max_size_over_limit():
    with given:
        max_size = 10
        buffer = StreamBuffer(max_size)
        text = "1234567890ABCDEF"  # 16 characters

    with when:
        buffer.write(text)

    with then:
        # Should keep only the last 10 characters
        assert buffer.get_value() == "7890ABCDEF"


def test_stream_buffer_with_max_size_progressive_writes():
    with given:
        max_size = 10
        buffer = StreamBuffer(max_size)

    with when:
        buffer.write("12345")
        buffer.write("67890")
        buffer.write("ABC")

    with then:
        # Total written: "1234567890ABC" (13 chars)
        # Should keep only the last 10 characters
        assert buffer.get_value() == "4567890ABC"


def test_stream_buffer_with_max_size_zero():
    with given:
        max_size = 0
        buffer = StreamBuffer(max_size)

    with when:
        buffer.write("Any text")

    with then:
        # With max_size=0, the implementation checks if max_size > 0
        # Since 0 is not > 0, no trimming occurs and text is kept
        assert buffer.get_value() == "Any text"


def test_stream_buffer_with_max_size_one():
    with given:
        max_size = 1
        buffer = StreamBuffer(max_size)

    with when:
        buffer.write("ABCDEF")

    with then:
        # Should keep only the last character
        assert buffer.get_value() == "F"


def test_stream_buffer_with_max_size_multiple_overwrites():
    with given:
        max_size = 5
        buffer = StreamBuffer(max_size)

    with when:
        buffer.write("ABCDEFGHIJ")  # 10 chars, keeps last 5: "FGHIJ"
        buffer.write("KLMNOP")      # 6 more chars, keeps last 5: "LMNOP"

    with then:
        assert buffer.get_value() == "LMNOP"


def test_stream_buffer_with_unicode_characters():
    with given:
        buffer = StreamBuffer()
        text = "Hello 世界 🌍"

    with when:
        buffer.write(text)

    with then:
        assert buffer.get_value() == text


def test_stream_buffer_with_unicode_and_max_size():
    with given:
        max_size = 5
        buffer = StreamBuffer(max_size)
        text = "Hello 世界"

    with when:
        buffer.write(text)

    with then:
        # Should keep the last 5 characters
        assert buffer.get_value() == "lo 世界"


def test_stream_buffer_with_newlines():
    with given:
        buffer = StreamBuffer()
        text = "Line 1\nLine 2\nLine 3"

    with when:
        buffer.write(text)

    with then:
        assert buffer.get_value() == text


def test_stream_buffer_with_newlines_and_max_size():
    with given:
        max_size = 10
        buffer = StreamBuffer(max_size)
        text = "Line 1\nLine 2\nLine 3"  # 20 characters total

    with when:
        buffer.write(text)

    with then:
        # Should keep only the last 10 characters
        assert buffer.get_value() == "e 2\nLine 3"
