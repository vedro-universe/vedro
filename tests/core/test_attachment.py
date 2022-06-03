from baby_steps import given, then, when
from pytest import raises

from vedro.core import Attachment


def test_attachment():
    with given:
        name = "log"
        mime_type = "text/plain"
        data = b""

    with when:
        attachment = Attachment(name, mime_type, data)

    with then:
        assert attachment.name == name
        assert attachment.mime_type == mime_type
        assert attachment.data == data


def test_attachment_repr():
    with given:
        name = "log"
        mime_type = "text/plain"
        data = b""

    with when:
        attachment = Attachment(name, mime_type, data)

    with then:
        assert repr(attachment) == f"Attachment<{name!r}, {mime_type!r}, size={len(data)}>"


def test_attachment_binary():
    with raises(Exception) as exc_info:
        Attachment("log", "text/plain", "text")

    with then:
        assert exc_info.type is AssertionError
