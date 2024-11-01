import json
import os
from functools import partial
from pathlib import Path
from tempfile import NamedTemporaryFile as TemporaryFile
from typing import Any, Callable, Dict, Union, cast

from filelock import FileLock
from niltype import Nil

from vedro.core import Plugin

__all__ = ("LocalStorage",)


LockFactory = Callable[[Path], FileLock]
_lock_factory: LockFactory = partial(FileLock, timeout=0.1)


class LocalStorage:
    """
    A class that represents local storage using a JSON file. This class is experimental and
    may be subject to changes in future versions.

    This class uses file locking to prevent concurrent access to the file. It loads the storage
    content from the file only on the first access, and all subsequent operations are performed
    in memory for performance reasons. Therefore, to write changes to the file, you need to call
    the 'flush' method explicitly.
    """

    def __init__(self, plugin: Plugin, project_dir: Path, *,
                 lock_factory: LockFactory = _lock_factory) -> None:
        """
        Initialize a new instance of LocalStorage.

        :param plugin: Plugin instance that provides namespace for the storage file.
        :param project_dir: The root directory of the project.
        :param lock_factory: Factory function to create a file lock.
        """
        namespace = f"{plugin.__class__.__name__}"
        self._dir_path = (project_dir / ".vedro" / "local_storage/").resolve()
        self._file_path = self._dir_path / f"{namespace}.json"
        self._lock_path = self._dir_path / f"{namespace}.lock"
        self._lock_factory = lock_factory
        self._lock: Union[FileLock, None] = None
        self._storage: Union[Dict[str, Any], None] = None

    async def get(self, key: str) -> Any:
        """
        Get the value associated with the key from the storage. This method loads the storage
        content from the file only on the first access.

        :param key: Key of the item to get from the storage.
        :return: The value associated with the key. If key does not exist, Nil is returned.
        """
        await self._ensure_storage_loaded()
        assert self._storage is not None  # for type checker
        return self._storage.get(key, Nil)

    async def put(self, key: str, value: Any) -> None:
        """
        Store the key-value pair in the storage. This method does not write the changes to the
        file. To save changes to the file, you need to call the 'flush' method explicitly.

        :param key: Key of the item to store.
        :param value: Value of the item to store.
        """
        await self._ensure_storage_loaded()
        assert self._storage is not None  # for type checker
        self._storage[key] = value

    async def flush(self) -> None:
        """
        Write the current state of the storage to the file.
        """
        await self._ensure_storage_loaded()
        await self._save_storage()

    def _acquire_lock(self) -> FileLock:
        """
        Acquire a file lock to prevent concurrent access to the storage file.

        :return: FileLock instance.
        """
        if self._lock is None:
            self._dir_path.mkdir(parents=True, exist_ok=True)
            self._lock = self._lock_factory(self._lock_path)
        return self._lock

    async def _ensure_storage_loaded(self) -> None:
        """
        Ensure that the storage data is loaded from the file. If the storage is not loaded,
        it loads the storage.
        """
        if self._storage is None:
            self._storage = await self._load_storage()

    async def _load_storage(self) -> Dict[str, Any]:
        """
        Load the storage data from the file.
        If the file does not exist, an empty dictionary is returned.

        :return: Dictionary that represents the storage.
        """
        with self._acquire_lock():
            try:
                with open(self._file_path, "r") as f:
                    return cast(Dict[str, Any], json.load(f))
            except FileNotFoundError:
                return {}
            except json.JSONDecodeError:
                print(f"Failed to load local storage from {self._file_path}")
                return {}

    async def _save_storage(self) -> None:
        """
        Save the current state of the storage to the file.
        """
        with self._acquire_lock():
            with TemporaryFile("w", dir=str(self._dir_path), suffix=".tmp", delete=False) as f:
                tmp_file_name = f.name
                json.dump(self._storage, f, indent=4, ensure_ascii=False)
            try:
                os.replace(tmp_file_name, self._file_path)
            except Exception:
                os.unlink(tmp_file_name)
