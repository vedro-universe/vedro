from pathlib import Path

import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro.core import Config, ConfigFileLoader


@pytest.fixture()
def config_path(tmp_path: Path) -> Path:
    return tmp_path / "vedro.cfg.py"


async def test_config_file_loader(*, config_path: Path):
    with given:
        loader = ConfigFileLoader(config := Config)

        config_path.write_text("\n".join([
            "import vedro",
            "class Config(vedro.Config):",
            "    pass",
        ]))

    with when:
        res = await loader.load(config_path)

    with then:
        assert res != config


async def test_config_file_loader_empty_file(*, config_path: Path):
    with given:
        loader = ConfigFileLoader(config := Config)

        config_path.write_text("")

    with when:
        res = await loader.load(config_path)

    with then:
        assert res == config


async def test_config_file_loader_not_exist(*, config_path: Path):
    with given:
        loader = ConfigFileLoader(config := Config)

    with when:
        res = await loader.load(config_path)

    with then:
        assert res == config


async def test_config_file_loader_with_invalid_class_name(*, config_path: Path):
    with given:
        loader = ConfigFileLoader(Config)

        config_path.write_text("\n".join([
            "import vedro",
            "class Cfg(vedro.Config):",
            "    pass",
        ]))

    with when, raises(BaseException) as exc:
        await loader.load(config_path)

    with then:
        assert exc.type is ValueError
        assert str(exc.value) == f"'Cfg' in '{config_path}' must be named 'Config'"


async def test_config_file_loader_without_inheriting_config(*, config_path: Path):
    with given:
        loader = ConfigFileLoader(Config)

        config_path.write_text("\n".join([
            "class Config:",
            "    pass",
        ]))

    with when, raises(BaseException) as exc:
        await loader.load(config_path)

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == f"'Config' in '{config_path}' must inherit from 'vedro.Config'"


async def test_config_file_loader_with_other_classes(*, config_path: Path):
    with given:
        loader = ConfigFileLoader(config := Config)

        config_path.write_text("\n".join([
            "import vedro",
            "class LocalConfig:",
            "    pass",
            "class Config(vedro.Config):",
            "    pass",
        ]))

    with when:
        res = await loader.load(config_path)

    with then:
        assert res != config
