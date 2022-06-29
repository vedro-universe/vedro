from pathlib import Path

import pytest
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


def test_memory_artifact_eq():
    with given:
        name, mime_type, data = "log", "text/plain", b""
        artifact1 = MemoryArtifact(name, mime_type, data)
        artifact2 = MemoryArtifact(name, mime_type, data)

    with when:
        is_eq = artifact1 == artifact2

    with then:
        assert is_eq


@pytest.mark.parametrize("args", [
    {"name": "not_log"},
    {"mime_type": "text/html"},
    {"data": b"<text>"},
])
def test_memory_artifact_not_eq(args):
    with given:
        args1 = {"name": "log", "mime_type": "text/plain", "data": b""}
        args2 = {**args1, **args}
        artifact1 = MemoryArtifact(**args1)
        artifact2 = MemoryArtifact(**args2)

    with when:
        is_eq = artifact1 == artifact2

    with then:
        assert not is_eq


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
        assert repr(artifact) == f"FileArtifact<{name!r}, {mime_type!r}, {path!r}>"


def test_file_artifact_path_only():
    with raises(Exception) as exc_info:
        FileArtifact("log", "text/plain", "./log.txt")

    with then:
        assert exc_info.type is AssertionError


def test_file_artifact_eq():
    with given:
        name, mime_type, data = "log", "text/plain", Path()
        artifact1 = FileArtifact(name, mime_type, data)
        artifact2 = FileArtifact(name, mime_type, data)

    with when:
        is_eq = artifact1 == artifact2

    with then:
        assert is_eq


@pytest.mark.parametrize("args", [
    {"name": "not_log"},
    {"mime_type": "text/html"},
    {"path": Path("/tmp")},
])
def test_file_artifact_not_eq(args):
    with given:
        args1 = {"name": "log", "mime_type": "text/plain", "path": Path()}
        args2 = {**args1, **args}
        artifact1 = FileArtifact(**args1)
        artifact2 = FileArtifact(**args2)

    with when:
        is_eq = artifact1 == artifact2

    with then:
        assert not is_eq
