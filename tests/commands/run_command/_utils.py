from argparse import Namespace
from os import chdir, linesep
from pathlib import Path
from unittest.mock import Mock

import pytest

from vedro.commands import CommandArgumentParser

__all__ = ("tmp_dir", "create_scenario", "arg_parser_",)


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


@pytest.fixture()
def arg_parser_() -> Mock:
    return Mock(CommandArgumentParser, parse_known_args=(Namespace(), []))
