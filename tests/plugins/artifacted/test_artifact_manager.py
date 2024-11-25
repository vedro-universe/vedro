from pathlib import Path

from baby_steps import given, when, then
from pytest import raises

from vedro.core import Artifact
from vedro.plugins.artifacted import ArtifactManager
from ._utils import (project_dir, create_memory_artifact, create_file_artifact, artifact_manager,
                     artifacts_dir)

__all__ = ("project_dir", "artifacts_dir", "artifact_manager")  # fixtures


def test_cleanup_artifacts(artifact_manager: ArtifactManager, artifacts_dir: Path):
    with given:
        artifacts_dir.mkdir(parents=True, exist_ok=True)

    with when:
        artifact_manager.cleanup_artifacts()

    with then:
        assert not artifacts_dir.exists()


def test_save_memory_artifact(artifact_manager: ArtifactManager, artifacts_dir: Path):
    with given:
        file_content = "Hello, World!"
        artifact = create_memory_artifact(file_content)

    with when:
        artifact_path = artifact_manager.save_artifact(artifact, artifacts_dir)

    with then:
        assert artifact_path.exists()
        assert artifact_path.read_bytes() == file_content.encode()


def test_save_file_artifact(artifact_manager: ArtifactManager, artifacts_dir: Path):
    with given:
        file_path = artifacts_dir / "file_artifact.txt"
        file_content = "Hello, World!"
        artifact = create_file_artifact(file_path, file_content)

    with when:
        artifact_path = artifact_manager.save_artifact(artifact, artifacts_dir)

    with then:
        assert artifact_path.exists()
        assert artifact_path.read_bytes() == file_content.encode()

        assert file_path.exists()
        assert file_path.read_bytes() == file_content.encode()


def test_save_artifact_unknown_type(artifact_manager: ArtifactManager, artifacts_dir: Path):
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
