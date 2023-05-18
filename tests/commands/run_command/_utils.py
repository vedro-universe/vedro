from os import chdir, linesep
from pathlib import Path

import pytest

__all__ = ("tmp_dir", "create_scenario",)


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    chdir(tmp_path)
    Path("./scenarios").mkdir(exist_ok=True)
    yield tmp_path


def create_scenario(tmp_dir: Path, scenario_path: str) -> None:
    scenario = linesep.join([
        "import vedro",
        "class Scenario(vedro.Scenario):",
        "   pass",
    ])
    (tmp_dir / "scenarios" / scenario_path).write_text(scenario)
