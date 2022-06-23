from abc import ABC
from pathlib import Path
from typing import Any

__all__ = ("Artifact", "MemoryArtifact", "FileArtifact",)


class Artifact(ABC):
    pass


class MemoryArtifact(Artifact):
    def __init__(self, name: str,  mime_type: str, data: bytes) -> None:
        assert isinstance(data, bytes)
        self._name = name
        self._data = data
        self._mime_type = mime_type

    @property
    def name(self) -> str:
        return self._name

    @property
    def mime_type(self) -> str:
        return self._mime_type

    @property
    def data(self) -> bytes:
        return self._data

    def __repr__(self) -> str:
        size = len(self._data)
        return f"{self.__class__.__name__}<{self._name!r}, {self._mime_type!r}, size={size}>"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and (self.__dict__ == other.__dict__)


class FileArtifact(Artifact):
    def __init__(self, name: str, mime_type: str, path: Path) -> None:
        assert isinstance(path, Path)
        self._name = name
        self._path = path
        self._mime_type = mime_type

    @property
    def name(self) -> str:
        return self._name

    @property
    def mime_type(self) -> str:
        return self._mime_type

    @property
    def path(self) -> Path:
        return self._path

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}<{self._name!r}, {self._mime_type!r}, {self._path!r}>"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and (self.__dict__ == other.__dict__)
