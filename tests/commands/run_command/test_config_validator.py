from pathlib import Path

import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro.commands.run_command._config_validator import ConfigValidator
from vedro.core import Config

from ._utils import tmp_dir

__all__ = ("tmp_dir",)  # fixtures


def test_validate():
    with given:
        class CustomScenarioDir(Config):
            pass

        validator = ConfigValidator(CustomScenarioDir)

    with when:
        res = validator.validate()

    with then:
        assert res is None


def test_validate_with_invalid_scenario_dir():
    with given:
        class CustomScenarioDir(Config):
            default_scenarios_dir = None

        validator = ConfigValidator(CustomScenarioDir)

    with when, raises(BaseException) as exc:
        validator.validate()

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == (
            "Expected `default_scenarios_dir` to be a Path, got <class 'NoneType'> (None)"
        )


@pytest.mark.usefixtures(tmp_dir.__name__)
def test_validate_with_nonexistent_scenario_dir():
    with given:
        class CustomScenarioDir(Config):
            default_scenarios_dir = "nonexisting/"

        validator = ConfigValidator(CustomScenarioDir)

    with when, raises(BaseException) as exc:
        validator.validate()

    with then:
        assert exc.type is FileNotFoundError

        scenarios_dir = Path(CustomScenarioDir.default_scenarios_dir).resolve()
        assert str(exc.value) == f"`default_scenarios_dir` ('{scenarios_dir}') does not exist"


def test_validate_with_non_directory_scenario_dir(tmp_dir: Path):
    with given:
        existing_file = tmp_dir / "scenario.py"
        existing_file.touch()

        class CustomScenarioDir(Config):
            default_scenarios_dir = existing_file

        validator = ConfigValidator(CustomScenarioDir)

    with when, raises(BaseException) as exc:
        validator.validate()

    with then:
        assert exc.type is NotADirectoryError
        assert str(exc.value) == f"`default_scenarios_dir` ('{existing_file}') is not a directory"


@pytest.mark.usefixtures(tmp_dir.__name__)
def test_validate_with_scenario_dir_outside_project_dir():
    with given:
        class CustomScenarioDir(Config):
            default_scenarios_dir = "/tmp"

        validator = ConfigValidator(CustomScenarioDir)

    with when, raises(BaseException) as exc:
        validator.validate()

    with then:
        assert exc.type is ValueError

        scenario_dir = Path(CustomScenarioDir.default_scenarios_dir).resolve()
        assert str(exc.value) == (
            f"`default_scenarios_dir` ('{scenario_dir}') must be inside project directory "
            f"('{Config.project_dir}')"
        )
