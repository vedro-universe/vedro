import os
from os import linesep
from pathlib import Path

import pytest

from vedro.commands import CommandArgumentParser

__all__ = ("tmp_dir", "create_scenario", "arg_parser",)


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    cwd = os.getcwd()
    try:
        os.chdir(tmp_path)

        Path("./scenarios").mkdir(exist_ok=True)
        yield tmp_path
    finally:
        os.chdir(cwd)


def create_scenario(tmp_dir: Path, scenario_path: str) -> None:
    scenario = linesep.join([
        "import vedro",
        "class Scenario(vedro.Scenario):",
        "   pass",
    ])
    (tmp_dir / "scenarios" / scenario_path).write_text(scenario)


class ArgumentParser(CommandArgumentParser):
    def parse_known_args(self, *args, **kwargs):
        return super().parse_known_args([], None)


@pytest.fixture()
def arg_parser() -> ArgumentParser:
    return ArgumentParser()
