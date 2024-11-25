import shutil
from os import linesep
from pathlib import Path
from typing import Callable, Type, Union

from vedro.core import Artifact, FileArtifact, MemoryArtifact

__all__ = ("ArtifactManager", "ArtifactManagerFactory",)


class ArtifactManager:
    def __init__(self, artifacts_dir: Path, project_dir: Path) -> None:
        self._artifacts_dir = artifacts_dir
        self._project_dir = project_dir

    def cleanup_artifacts(self) -> None:
        if not self._artifacts_dir.exists():
            return

        try:
            shutil.rmtree(self._artifacts_dir)
        except FileNotFoundError:
            # The directory was deleted between the check and the rmtree call
            pass
        except PermissionError as e:
            raise self._make_permissions_error(
                f"Failed to clean up artifacts directory '{self._artifacts_dir}'."
            ) from e
        except OSError as e:
            raise OSError(
                f"Failed to clean up artifacts directory '{self._artifacts_dir}': {e}"
            ) from e

    def save_artifact(self, artifact: Artifact, path: Path) -> Path:
        self._ensure_directory_exists(path)

        if isinstance(artifact, MemoryArtifact):
            return self._save_memory_artifact(artifact, path)
        elif isinstance(artifact, FileArtifact):
            return self._save_file_artifact(artifact, path)
        else:
            artifact_type = type(artifact).__name__
            message = f"Can't save artifact to '{path}': unknown type '{artifact_type}'"
            raise TypeError(message)

    def _ensure_directory_exists(self, path: Path) -> None:
        if not path.exists():
            try:
                path.mkdir(parents=True, exist_ok=True)
            except PermissionError as e:
                raise self._make_permissions_error(f"Failed to create directory '{path}'.") from e
            except OSError as e:
                raise OSError(f"Failed to create directory '{path}': {e}") from e

    def _save_memory_artifact(self, artifact: MemoryArtifact, path: Path) -> Path:
        artifact_dest = (path / artifact.name).resolve()
        try:
            artifact_dest.write_bytes(artifact.data)
        except PermissionError as e:
            raise self._make_permissions_error(
                f"Permission denied when writing to '{artifact_dest}'."
            ) from e
        except OSError as e:
            raise OSError(f"Failed to write MemoryArtifact to '{artifact_dest}': {e}") from e
        else:
            return artifact_dest

    def _save_file_artifact(self, artifact: FileArtifact, path: Path) -> Path:
        artifact_dest = (path / artifact.name).resolve()
        artifact_source = artifact.path
        if not artifact_source.is_absolute():
            artifact_source = (self._project_dir / artifact_source).resolve()
        try:
            shutil.copy2(artifact_source, artifact_dest)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Source file '{artifact_source}' not found: {e}") from e
        except PermissionError as e:
            raise self._make_permissions_error(
                f"Permission denied when copying from '{artifact_source}' to '{artifact_dest}'."
            ) from e
        except OSError as e:
            raise OSError(
                f"Failed to copy FileArtifact from '{artifact_source}' to '{artifact_dest}': {e}"
            ) from e
        else:
            return artifact_dest

    def _make_permissions_error(self, failure_message: str) -> PermissionError:
        return PermissionError(linesep.join([
            failure_message,
            "To resolve this issue, you can:",
            "- Adjust the directory permissions to allow write access.",
            "- Change the target directory to one with the appropriate permissions.",
            "- Disable saving artifacts."
        ]))


ArtifactManagerFactory = Union[
    Type[ArtifactManager],
    Callable[[Path, Path], ArtifactManager]
]
