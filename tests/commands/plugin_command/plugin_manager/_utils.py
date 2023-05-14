from os import chdir, linesep
from pathlib import Path
from time import time
from typing import List

__all__ = ("create_config", "read_config")


def create_config(tmp_path: Path, config: List[str]) -> Path:
    chdir(tmp_path)
    now = int(time() * 1000)
    config_file = Path(f"vedro-cfg-{now}.py")
    config_file.write_text(linesep.join(config))
    return config_file


def read_config(config_path: Path) -> str:
    return config_path.read_text()