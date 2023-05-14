import sys
from os import linesep
from pathlib import Path

import pytest
from baby_steps import given, then, when

from vedro.commands.plugin_command.plugin_manager import PluginManager

from ._utils import create_config, read_config


@pytest.mark.asyncio
@pytest.mark.skipif(sys.version_info < (3, 8), reason="requires python3.8 or higher")
async def test_plugin_manager_no_file(tmp_path: Path):
    with given:
        config_path = create_config(tmp_path)
        plugin_manager = PluginManager(config_path)

    with when:
        await plugin_manager.enable("tagger")

    with then:
        config = read_config(config_path)
        assert config == linesep.join([
            "import vedro",
            "import vedro.plugins.tagger",
            "",
            "",
            "class Config(vedro.Config):",
            "",
            "    class Plugins(vedro.Config.Plugins):",
            "",
            "        class Tagger(vedro.plugins.tagger.Tagger):",
            "            enabled = True",
            "",
        ])


@pytest.mark.asyncio
@pytest.mark.skipif(sys.version_info < (3, 8), reason="requires python3.8 or higher")
async def test_plugin_manager_no_config(tmp_path: Path):
    with given:
        config_path = create_config(tmp_path, [])
        plugin_manager = PluginManager(config_path)

    with when:
        await plugin_manager.enable("tagger")

    with then:
        config = read_config(config_path)
        assert config == linesep.join([
            "import vedro",
            "import vedro.plugins.tagger",
            "",
            "",
            "class Config(vedro.Config):",
            "",
            "    class Plugins(vedro.Config.Plugins):",
            "",
            "        class Tagger(vedro.plugins.tagger.Tagger):",
            "            enabled = True",
            "",
        ])


@pytest.mark.asyncio
@pytest.mark.skipif(sys.version_info < (3, 8), reason="requires python3.8 or higher")
async def test_plugin_manager_no_plugins_section(tmp_path: Path):
    with given:
        config_path = create_config(tmp_path, [
            "import vedro",
            "",
            "",
            "class Config(vedro.Config):",
            "    pass",
        ])
        plugin_manager = PluginManager(config_path)

    with when:
        await plugin_manager.enable("tagger")

    with then:
        config = read_config(config_path)
        assert config == linesep.join([
            "import vedro.plugins.tagger",
            "import vedro",
            "",
            "",
            "class Config(vedro.Config):",
            "    pass",
            "",
            "    class Plugins(vedro.Config.Plugins):",
            "",
            "        class Tagger(vedro.plugins.tagger.Tagger):",
            "            enabled = True",
            "",
        ])


@pytest.mark.asyncio
@pytest.mark.skipif(sys.version_info < (3, 8), reason="requires python3.8 or higher")
async def test_plugin_manager_no_plugins(tmp_path: Path):
    with given:
        config_path = create_config(tmp_path, [
            "import vedro",
            "",
            "",
            "class Config(vedro.Config):",
            "",
            "    class Plugins(vedro.Config.Plugins):",
            "        pass",
        ])
        plugin_manager = PluginManager(config_path)

    with when:
        await plugin_manager.enable("tagger")

    with then:
        config = read_config(config_path)
        assert config == linesep.join([
            "import vedro.plugins.tagger",
            "import vedro",
            "",
            "",
            "class Config(vedro.Config):",
            "",
            "    class Plugins(vedro.Config.Plugins):",
            "        pass",
            "",
            "        class Tagger(vedro.plugins.tagger.Tagger):",
            "            enabled = True",
            "",
        ])


@pytest.mark.asyncio
@pytest.mark.skipif(sys.version_info < (3, 8), reason="requires python3.8 or higher")
async def test_plugin_manager_no_target_plugin(tmp_path: Path):
    with given:
        config_path = create_config(tmp_path, [
            "import vedro",
            "import vedro.plugins.skipper",
            "import vedro.plugins.tagger",
            "",
            "",
            "class Config(vedro.Config):",
            "",
            "    class Plugins(vedro.Config.Plugins):",
            "",
            "        class Skipper(vedro.plugins.skipper.Skipper):",
            "            enabled = True",
            "",
        ])
        plugin_manager = PluginManager(config_path)

    with when:
        await plugin_manager.enable("tagger")

    with then:
        config = read_config(config_path)
        assert config == linesep.join([
            "import vedro",
            "import vedro.plugins.skipper",
            "import vedro.plugins.tagger",
            "",
            "",
            "class Config(vedro.Config):",
            "",
            "    class Plugins(vedro.Config.Plugins):",
            "",
            "        class Skipper(vedro.plugins.skipper.Skipper):",
            "            enabled = True",
            "",
            "        class Tagger(vedro.plugins.tagger.Tagger):",
            "            enabled = True",
            "",
        ])


@pytest.mark.asyncio
@pytest.mark.skipif(sys.version_info < (3, 8), reason="requires python3.8 or higher")
async def test_plugin_manager_no_enabled_attr(tmp_path: Path):
    with given:
        config_path = create_config(tmp_path, [
            "import vedro",
            "import vedro.plugins.skipper",
            "import vedro.plugins.tagger",
            "",
            "",
            "class Config(vedro.Config):",
            "",
            "    class Plugins(vedro.Config.Plugins):",
            "",
            "        class Tagger(vedro.plugins.tagger.Tagger):",
            "            description = 'desc'",
            "",
            "        class Skipper(vedro.plugins.skipper.Skipper):",
            "            enabled = True",
            "",
        ])
        plugin_manager = PluginManager(config_path)

    with when:
        await plugin_manager.enable("tagger")

    with then:
        config = read_config(config_path)
        assert config == linesep.join([
            "import vedro",
            "import vedro.plugins.skipper",
            "import vedro.plugins.tagger",
            "",
            "",
            "class Config(vedro.Config):",
            "",
            "    class Plugins(vedro.Config.Plugins):",
            "",
            "        class Tagger(vedro.plugins.tagger.Tagger):",
            "            description = 'desc'",
            "            enabled = True",
            "",
            "        class Skipper(vedro.plugins.skipper.Skipper):",
            "            enabled = True",
            "",
        ])


@pytest.mark.asyncio
@pytest.mark.skipif(sys.version_info < (3, 8), reason="requires python3.8 or higher")
@pytest.mark.parametrize("enabled", [True, False])
async def test_plugin_manager_enabled_enabled(enabled: bool, *, tmp_path: Path):
    with given:
        config_path = create_config(tmp_path, [
            "import vedro",
            "import vedro.plugins.tagger",
            "",
            "",
            "class Config(vedro.Config):",
            "",
            "    class Plugins(vedro.Config.Plugins):",
            "",
            "        class Tagger(vedro.plugins.tagger.Tagger):",
            f"            enabled = {enabled}",
            "",
        ])
        plugin_manager = PluginManager(config_path)

    with when:
        await plugin_manager.enable("tagger")

    with then:
        config = read_config(config_path)
        assert config == linesep.join([
            "import vedro",
            "import vedro.plugins.tagger",
            "",
            "",
            "class Config(vedro.Config):",
            "",
            "    class Plugins(vedro.Config.Plugins):",
            "",
            "        class Tagger(vedro.plugins.tagger.Tagger):",
            "            enabled = True",
            "",
        ])


@pytest.mark.asyncio
@pytest.mark.skipif(sys.version_info < (3, 8), reason="requires python3.8 or higher")
@pytest.mark.parametrize("enabled", [True, False])
async def test_plugin_manager_disabled_enabled(enabled: bool, *, tmp_path: Path):
    with given:
        config_path = create_config(tmp_path, [
            "import vedro",
            "import vedro.plugins.tagger",
            "",
            "",
            "class Config(vedro.Config):",
            "",
            "    class Plugins(vedro.Config.Plugins):",
            "",
            "        class Tagger(vedro.plugins.tagger.Tagger):",
            f"            enabled = {enabled}",
            "",
        ])
        plugin_manager = PluginManager(config_path)

    with when:
        await plugin_manager.disable("tagger")

    with then:
        config = read_config(config_path)
        assert config == linesep.join([
            "import vedro",
            "import vedro.plugins.tagger",
            "",
            "",
            "class Config(vedro.Config):",
            "",
            "    class Plugins(vedro.Config.Plugins):",
            "",
            "        class Tagger(vedro.plugins.tagger.Tagger):",
            "            enabled = False",
            "",
        ])
