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
            rel_path = self._get_rel_path(self._artifacts_dir)
            failure_message = f"Failed to clean up artifacts directory '{rel_path}'."
            raise self._make_permissions_error(failure_message) from e
        except OSError as e:
            rel_path = self._get_rel_path(self._artifacts_dir)
            raise OSError(f"Failed to cleanup artifacts directory '{rel_path}': {e}") from e

    def save_artifact(self, artifact: Artifact, path: Path) -> Path:
        try:
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)

            if isinstance(artifact, MemoryArtifact):
                artifact_dest = (path / artifact.name).resolve()
                artifact_dest.write_bytes(artifact.data)
                return artifact_dest

            elif isinstance(artifact, FileArtifact):
                artifact_dest = (path / artifact.name).resolve()
                artifact_source = artifact.path
                if not artifact_source.is_absolute():
                    artifact_source = (self._project_dir / artifact_source).resolve()
                shutil.copy2(artifact_source, artifact_dest)
                return artifact_dest

            else:
                artifact_type = type(artifact).__name__
                rel_path = self._get_rel_path(path)
                message = f"Can't save artifact to '{rel_path}': unknown type '{artifact_type}'"
                raise TypeError(message)
        except PermissionError as e:
            rel_path = self._get_rel_path(path)
            failure_message = f"Failed to save artifact to '{rel_path}'."
            raise self._make_permissions_error(failure_message) from e

    def _get_rel_path(self, path: Path) -> Path:
        return path.relative_to(self._project_dir)

    def _make_permissions_error(self, failure_message: str) -> PermissionError:
        return PermissionError(linesep.join([
            failure_message,
            "To resolve this issue, you can:",
            "- Adjust the directory permissions to allow write access.",
            "- Change the target directory to one with the appropriate permissions.",
            "- Disable saving artifacts by using the `--no-save-artifacts` option."
        ]))


ArtifactManagerFactory = Union[
    Type[ArtifactManager],
    Callable[[Path, Path], ArtifactManager]
]
