from abc import ABC
from pathlib import Path
from typing import Any

__all__ = ("Artifact", "MemoryArtifact", "FileArtifact",)


class Artifact(ABC):
    """
    The base class for representing artifacts in a system.

    An artifact in this context is a piece of data generated during the execution
    of a scenario or a step. It can be anything from log files, screenshots, to data dumps.
    This class serves as an abstract base class for different types of artifacts,
    such as MemoryArtifact and FileArtifact.
    """
    pass


class MemoryArtifact(Artifact):
    """
    Represents an artifact that is stored in memory.
    """

    def __init__(self, name: str,  mime_type: str, data: bytes) -> None:
        """
        Initialize a MemoryArtifact with a name, MIME type, and data.

        :param name: The name of the artifact.
        :param mime_type: The MIME type of the data.
        :param data: The actual data in bytes.
        """
        if not isinstance(data, bytes):
            raise TypeError("'data' must be of type bytes")
        self._name = name
        self._data = data
        self._mime_type = mime_type

    @property
    def name(self) -> str:
        """
        Get the name of the artifact.

        :return: The name of the artifact.
        """
        return self._name

    @property
    def mime_type(self) -> str:
        """
        Get the MIME type of the artifact data.

        :return: The MIME type as a string.
        """
        return self._mime_type

    @property
    def data(self) -> bytes:
        """
        Get the data stored in the artifact.

        :return: The data as bytes.
        """
        return self._data

    def __repr__(self) -> str:
        """
        Represent the MemoryArtifact as a string.

        :return: A string representation of the MemoryArtifact.
        """
        size = len(self._data)
        return f"{self.__class__.__name__}<{self._name!r}, {self._mime_type!r}, size={size}>"

    def __eq__(self, other: Any) -> bool:
        """
        Check equality with another MemoryArtifact.

        :param other: The other MemoryArtifact to compare with.
        :return: True if the other artifact is equal to this one, False otherwise.
        """
        return isinstance(other, self.__class__) and (self.__dict__ == other.__dict__)


class FileArtifact(Artifact):
    """
    Represents an artifact that is stored as a file on the filesystem.
    """

    def __init__(self, name: str, mime_type: str, path: Path) -> None:
        """
        Initialize a FileArtifact with a name, MIME type, and file path.

        :param name: The name of the artifact.
        :param mime_type: The MIME type of the file.
        :param path: The path to the file.
        """
        if not isinstance(path, Path):
            raise TypeError("'path' must be an instance of pathlib.Path")
        self._name = name
        self._path = path
        self._mime_type = mime_type

    @property
    def name(self) -> str:
        """
        Get the name of the artifact.

        :return: The name of the artifact.
        """
        return self._name

    @property
    def mime_type(self) -> str:
        """
        Get the MIME type of the artifact data.

        :return: The MIME type as a string.
        """
        return self._mime_type

    @property
    def path(self) -> Path:
        """
        Get the file path of the artifact.

        :return: The path of the file as a Path object.
        """
        return self._path

    def __repr__(self) -> str:
        """
        Represent the FileArtifact as a string.

        :return: A string representation of the FileArtifact.
        """
        return f"{self.__class__.__name__}<{self._name!r}, {self._mime_type!r}, {self._path!r}>"

    def __eq__(self, other: Any) -> bool:
        """
        Check equality with another FileArtifact.

        :param other: The other FileArtifact to compare with.
        :return: True if the other artifact is equal to this one, False otherwise.
        """
        return isinstance(other, self.__class__) and (self.__dict__ == other.__dict__)
