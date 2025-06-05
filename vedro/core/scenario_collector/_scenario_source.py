from asyncio import Lock
from pathlib import Path
from types import ModuleType
from typing import Union

from vedro.core import ModuleLoader

__all__ = ("ScenarioSource",)


class ScenarioSource:
    def __init__(self, path: Path, project_dir: Path, module_loader: ModuleLoader) -> None:
        self._path = path
        self._project_dir = project_dir
        self._module_loader = module_loader
        self._module: Union[ModuleType, None] = None
        self._content: Union[str, None] = None
        self._lock = Lock()

    @property
    def path(self) -> Path:
        return self._path

    @property
    def rel_path(self) -> Path:
        if self._path.is_absolute():
            return self._path.relative_to(self._project_dir)
        return self._path

    @property
    def project_dir(self) -> Path:
        return self._project_dir

    async def get_module(self) -> ModuleType:
        async with self._lock:
            if self._module is None:
                self._module = await self._module_loader.load(self._path)
        return self._module

    async def get_content(self) -> str:
        async with self._lock:
            if self._content is None:
                self._content = self._path.read_text()
        return self._content
