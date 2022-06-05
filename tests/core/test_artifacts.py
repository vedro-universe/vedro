from pathlib import Path

from baby_steps import given, then, when
from pytest import raises

from vedro.core import FileArtifact, MemoryArtifact


def test_memory_artifact():
    with given:
        name = "log"
        mime_type = "text/plain"
        data = b""

    with when:
        artifact = MemoryArtifact(name, mime_type, data)

    with then:
        assert artifact.name == name
        assert artifact.mime_type == mime_type
        assert artifact.data == data


def test_memory_artifact_repr():
    with given:
        name = "log"
        mime_type = "text/plain"
        data = b""

    with when:
        artifact = MemoryArtifact(name, mime_type, data)

    with then:
        assert repr(artifact) == f"MemoryArtifact<{name!r}, {mime_type!r}, size={len(data)}>"


def test_memory_artifact_binary_only():
    with raises(Exception) as exc_info:
        MemoryArtifact("log", "text/plain", "text")

    with then:
        assert exc_info.type is AssertionError


def test_file_artifact():
    with given:
        name = "log"
        mime_type = "text/plain"
        path = Path()

    with when:
        artifact = FileArtifact(name, mime_type, path)

    with then:
        assert artifact.name == name
        assert artifact.mime_type == mime_type
        assert artifact.path == path


def test_file_artifact_repr():
    with given:
        name = "log"
        mime_type = "text/plain"
        path = Path()

    with when:
        artifact = FileArtifact(name, mime_type, path)

    with then:
        print(repr(artifact))
        assert repr(artifact) == f"FileArtifact<{name!r}, {mime_type!r}, {path!r}>"


def test_file_artifact_path_only():
    with raises(Exception) as exc_info:
        FileArtifact("log", "text/plain", "./log.txt")

    with then:
        assert exc_info.type is AssertionError
