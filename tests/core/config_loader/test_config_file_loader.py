from pathlib import Path

import pytest
from baby_steps import given, then, when

from vedro.core import Config, ConfigFileLoader


@pytest.mark.asyncio
async def test_config_file_loader(*, tmp_path: Path):
    with given:
        config = Config
        loader = ConfigFileLoader(config)
        path = tmp_path / "vedro.cfg.py"
        path.write_text("\n".join([
            "import vedro",
            "class Config(vedro.Config):",
            "    pass",
        ]))

    with when:
        res = await loader.load(path)

    with then:
        assert res != config


@pytest.mark.asyncio
async def test_config_file_loader_empty_file(*, tmp_path: Path):
    with given:
        config = Config
        loader = ConfigFileLoader(config)
        path = tmp_path / "vedro.cfg.py"
        path.write_text("")

    with when:
        res = await loader.load(path)

    with then:
        assert res == config


@pytest.mark.asyncio
async def test_config_file_loader_not_exist(*, tmp_path: Path):
    with given:
        config = Config
        loader = ConfigFileLoader(config)
        path = tmp_path / "vedro.cfg.py"

    with when:
        res = await loader.load(path)

    with then:
        assert res == config
