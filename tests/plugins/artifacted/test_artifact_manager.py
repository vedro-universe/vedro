from pathlib import Path
from typing import Type
from unittest.mock import call

import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro.core import Artifact
from vedro.plugins.artifacted import ArtifactManager

from ._utils import (
    artifact_manager,
    artifacts_dir,
    create_file_artifact,
    create_memory_artifact,
    patch_copy2,
    patch_mkdir,
    patch_rmtree,
    patch_write_bytes,
    project_dir,
)

__all__ = ("project_dir", "artifacts_dir", "artifact_manager")  # fixtures


def test_cleanup_artifacts(*, artifact_manager: ArtifactManager, artifacts_dir: Path):
    with given:
        artifacts_dir.mkdir(parents=True, exist_ok=True)

    with when:
        artifact_manager.cleanup_artifacts()

    with then:
        assert not artifacts_dir.exists()


def test_cleanup_artifacts_file_not_found(*, artifact_manager: ArtifactManager,
                                          artifacts_dir: Path):
    with given:
        artifacts_dir.mkdir(parents=True, exist_ok=True)

    with when, patch_rmtree(FileNotFoundError()) as mock:
        artifact_manager.cleanup_artifacts()

    with then:
        # no exception raised
        assert mock.mock_calls == [call(artifacts_dir)]


@pytest.mark.parametrize("exc_type", [PermissionError, OSError])
def test_cleanup_artifacts_os_error(exc_type: Type[Exception], *,
                                    artifact_manager: ArtifactManager, artifacts_dir: Path):
    with given:
        artifacts_dir.mkdir(parents=True, exist_ok=True)

    with when, \
         patch_rmtree(exc_type()) as mock, \
         raises(Exception) as exc:
        artifact_manager.cleanup_artifacts()

    with then:
        assert exc.type is exc_type
        assert "Failed to clean up artifacts directory" in str(exc.value)

        assert mock.mock_calls == [call(artifacts_dir)]


def test_save_memory_artifact(*, artifact_manager: ArtifactManager, artifacts_dir: Path):
    with given:
        file_content = "Hello, World!"
        artifact = create_memory_artifact(file_content)

    with when:
        artifact_path = artifact_manager.save_artifact(artifact, artifacts_dir)

    with then:
        assert artifact_path.exists()
        assert artifact_path.read_bytes() == file_content.encode()


@pytest.mark.parametrize(("exc_type", "exc_msg"), [
    (PermissionError, "Permission denied when writing to"),
    (OSError, "Failed to write MemoryArtifact to"),
])
def test_save_memory_artifact_os_error(exc_type: Type[Exception], exc_msg: str, *,
                                       artifact_manager: ArtifactManager, artifacts_dir: Path):
    with given:
        file_content = "Hello, World!"
        artifact = create_memory_artifact(file_content)

    with when, \
         patch_write_bytes(exc_type()) as mock, \
         raises(Exception) as exc:
        artifact_manager.save_artifact(artifact, artifacts_dir)

    with then:
        assert exc.type is exc_type
        assert exc_msg in str(exc.value)

        assert mock.mock_calls == [call(file_content.encode())]


def test_save_file_artifact(*, artifact_manager: ArtifactManager,
                            artifacts_dir: Path, tmp_path: Path):
    with given:
        file_path = tmp_path / "file_artifact.txt"
        file_content = "Hello, World!"
        artifact = create_file_artifact(file_path, file_content)

    with when:
        artifact_path = artifact_manager.save_artifact(artifact, artifacts_dir)

    with then:
        assert artifact_path.exists()
        assert artifact_path.read_bytes() == file_content.encode()

        assert artifact.path.exists()
        assert artifact.path.read_bytes() == file_content.encode()


@pytest.mark.parametrize(("exc_type", "exc_msg"), [
    (FileNotFoundError, "Source file"),
    (PermissionError, "Permission denied when copying from "),
    (OSError, "Failed to copy FileArtifact from"),
])
def test_save_file_artifact_os_error(exc_type: Type[Exception], exc_msg: str, *,
                                     artifact_manager: ArtifactManager,
                                     artifacts_dir: Path,
                                     tmp_path: Path):
    with given:
        file_path = tmp_path / "file_artifact.txt"
        file_content = "Hello, World!"
        artifact = create_file_artifact(file_path, file_content)

    with when, \
         patch_copy2(exc_type()) as mock, \
         raises(Exception) as exc:
        artifact_manager.save_artifact(artifact, artifacts_dir)

    with then:
        assert exc.type is exc_type
        assert exc_msg in str(exc.value)

        assert artifact.path.exists()
        assert artifact.path.read_bytes() == file_content.encode()

        assert mock.mock_calls == [call(artifact.path, artifacts_dir / artifact.name)]


@pytest.mark.parametrize("exc_type", [PermissionError, OSError])
def test_save_artifact_directory_mkdir_failure(exc_type: Type[Exception], *,
                                               artifact_manager: ArtifactManager,
                                               artifacts_dir: Path):
    with given:
        artifacts_dir.rmdir()  # artifacts_dir is automatically created by the fixture

        file_content = "Hello, World!"
        artifact = create_memory_artifact(file_content)

    with when, \
         patch_mkdir(exc_type()) as mock, \
         raises(Exception) as exc:
        artifact_manager.save_artifact(artifact, artifacts_dir)

    with then:
        assert exc.type is exc_type
        assert "Failed to create directory" in str(exc.value)

        assert mock.mock_calls == [call(parents=True, exist_ok=True)]


def test_save_artifact_unknown_type(*, artifact_manager: ArtifactManager, artifacts_dir: Path):
    with given:
        class UnknownArtifact(Artifact):
            pass

        artifact = UnknownArtifact()

    with when, raises(BaseException) as exc:
        artifact_manager.save_artifact(artifact, artifacts_dir)

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == (
            f"Can't save artifact to '{artifacts_dir}': unknown type 'UnknownArtifact'"
        )
