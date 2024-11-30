import shutil
from os import linesep
from pathlib import Path
from typing import Callable, Type, Union

from vedro.core import Artifact, FileArtifact, MemoryArtifact

__all__ = ("ArtifactManager", "ArtifactManagerFactory",)


class ArtifactManager:
    """
    Manages the creation, storage, and cleanup of artifacts.

    This class provides functionality to handle artifacts in the form of memory and file-based
    objects. It ensures proper directory structure, saves artifacts to a specified location,
    and handles cleanup operations for artifacts directories.
    """

    def __init__(self, artifacts_dir: Path, project_dir: Path) -> None:
        """
        Initialize the ArtifactManager with the specified directories.

        :param artifacts_dir: The directory where artifacts will be stored.
        :param project_dir: The base project directory, used to resolve relative paths
                            for file artifacts.
        """
        self._artifacts_dir = artifacts_dir
        self._project_dir = project_dir

    def cleanup_artifacts(self) -> None:
        """
        Remove all files and directories within the artifacts directory.

        Deletes the artifacts directory and its contents if it exists. Handles cases where
        the directory does not exist, or where permissions or other OS errors occur.

        :raises PermissionError: If the directory cannot be deleted due to permissions issues.
        :raises OSError: If an unexpected OS error occurs while deleting the directory.
        """
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
        """
        Save an artifact to the specified path.

        Depending on the type of artifact, this method saves either a memory-based artifact
        or a file-based artifact. Ensures that the target directory exists before saving.

        :param artifact: The artifact to save, which can be a MemoryArtifact or FileArtifact.
        :param path: The directory where the artifact should be saved.
        :return: The path to the saved artifact.
        :raises TypeError: If the artifact type is unknown.
        :raises PermissionError: If the directory or file cannot be created due to
                                 permissions issues.
        :raises OSError: If an unexpected OS error occurs during the save operation.
        """
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
        """
        Ensure that the specified directory exists, creating it if necessary.

        :param path: The directory to check or create.
        :raises PermissionError: If the directory cannot be created due to permissions issues.
        :raises OSError: If an unexpected OS error occurs while creating the directory.
        """
        if not path.exists():
            try:
                path.mkdir(parents=True, exist_ok=True)
            except PermissionError as e:
                raise self._make_permissions_error(f"Failed to create directory '{path}'.") from e
            except OSError as e:
                raise OSError(f"Failed to create directory '{path}': {e}") from e

    def _save_memory_artifact(self, artifact: MemoryArtifact, path: Path) -> Path:
        """
        Save a MemoryArtifact to the specified path.

        Writes the binary data from the MemoryArtifact to a file.

        :param artifact: The MemoryArtifact to save.
        :param path: The directory where the artifact should be saved.
        :return: The path to the saved artifact.
        :raises PermissionError: If writing to the file is denied.
        :raises OSError: If an unexpected OS error occurs while writing the file.
        """
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
        """
        Save a FileArtifact to the specified path.

        Copies the source file from the artifact's path to the target directory.

        :param artifact: The FileArtifact to save.
        :param path: The directory where the artifact should be saved.
        :return: The path to the saved artifact.
        :raises FileNotFoundError: If the source file does not exist.
        :raises PermissionError: If copying the file is denied.
        :raises OSError: If an unexpected OS error occurs while copying the file.
        """
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
        """
        Create a detailed PermissionError with resolution suggestions.

        :param failure_message: The main error message explaining the failure.
        :return: A PermissionError instance with additional context.
        """
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
