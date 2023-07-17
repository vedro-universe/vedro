from pathlib import Path

from ._local_storage import LocalStorage

local_storage = LocalStorage(Path(".vedro/local_storage"))

__all__ = ("local_storage", "LocalStorage",)
