from pathlib import Path
from types import ModuleType

import pytest
from _pytest.python_api import raises
from baby_steps import given, then, when

from vedro.core import ModuleFileLoader


def make_module(tmp_path: Path, name: str, content: str) -> Path:
    module_path = tmp_path / name
    module_path.write_text(content)
    return module_path


async def test_load_module(tmp_path: Path):
    with given:
        loader = ModuleFileLoader()
        module_path = make_module(tmp_path, "test_module.py", "x = 42")

    with when:
        module = await loader.load(module_path)

    with then:
        assert isinstance(module, ModuleType)
        assert module.x == 42


async def test_load_module_with_valid_name(tmp_path: Path):
    with given:
        loader = ModuleFileLoader(validate_module_names=True)
        rel_path = tmp_path.relative_to(Path.cwd())
        module_path = make_module(rel_path, "test_module.py", "x = 42")

    with when:
        module = await loader.load(module_path)

    with then:
        assert isinstance(module, ModuleType)
        assert module.x == 42


@pytest.mark.parametrize("name", ["123name", "import"])
async def test_load_module_with_invalid_name(tmp_path: Path, name: str):
    with given:
        loader = ModuleFileLoader(validate_module_names=True)
        rel_path = tmp_path.relative_to(Path.cwd())
        module_path = make_module(rel_path, f"{name}.py", "x = 42")

    with when, raises(BaseException) as exc:
        await loader.load(module_path)

    with then:
        assert exc.type is ValueError
        assert str(exc.value) == (
            f"The module name derived from the path '{module_path}' is invalid due to the segment "
            f"'{name}'. A valid module name should start with a letter or underscore, contain "
            "only letters, digits, or underscores, and not be a Python keyword."
        )


async def test_load_module_with_non_existent_path():
    with given:
        loader = ModuleFileLoader()
        non_existent_path = Path("non_existent_module.py")

    with when, raises(BaseException) as exc:
        await loader.load(non_existent_path)

    with then:
        assert exc.type is FileNotFoundError
        assert "[Errno 2] No such file or directory" in str(exc.value)
