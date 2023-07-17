import json
from pathlib import Path
from typing import Any, Dict, Union

from filelock import FileLock
from niltype import Nil

from vedro.core import Plugin

__all__ = ("LocalStorage",)


class LocalStorage:
    def __init__(self, directory: Path) -> None:
        self._directory = directory
        self._lock_file = self._directory / "__filelock__"
        self._lock_timeout = 1.0  # seconds
        self._lock: Union[FileLock, None] = None
        self._storage: Dict[str, Dict[str, Any]] = {}

    async def get(self, key: str, plugin: Plugin) -> Any:
        namespace = self._get_namespace(plugin)
        await self._ensure_namespace_loaded(namespace)
        return self._storage[namespace].get(key, Nil)

    async def put(self, key: str, value: Any, plugin: Plugin) -> None:
        namespace = self._get_namespace(plugin)
        await self._ensure_namespace_loaded(namespace)
        self._storage[namespace][key] = value

    async def flush(self, plugin: Plugin) -> None:
        namespace = self._get_namespace(plugin)
        await self._ensure_namespace_loaded(namespace)
        await self._save_storage(namespace, self._storage[namespace])

    def _aquire_lock(self) -> FileLock:
        if self._lock is None:
            self._directory.mkdir(parents=True, exist_ok=True)
            self._lock = FileLock(self._lock_file, timeout=self._lock_timeout)
        return self._lock

    def _get_namespace(self, plugin: Plugin) -> str:
        return f"{plugin.__class__.__name__}"

    def _get_filename(self, namespace: str) -> Path:
        return self._directory / f"{namespace}.json"

    async def _ensure_namespace_loaded(self, namespace: str) -> None:
        if namespace not in self._storage:
            self._storage[namespace] = await self._load_storage(namespace)

    async def _load_storage(self, namespace: str) -> Dict[str, Any]:
        filename = self._get_filename(namespace)
        with self._aquire_lock():
            try:
                with open(filename, "r") as f:
                    return json.load(f)  # type: ignore
            except FileNotFoundError:
                return {}

    async def _save_storage(self, namespace: str, payload: Dict[str, Any]) -> None:
        filename = self._get_filename(namespace)
        with self._aquire_lock():
            with open(filename, "w") as f:
                json.dump(payload, f, indent=4, ensure_ascii=False)
