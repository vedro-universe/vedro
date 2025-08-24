from pathlib import Path
from typing import List

from vedro.core import ScenarioFileFinder
from vedro.core.scenario_finder.scenario_file_finder import DunderFilter, HiddenFilter


def _create_file_tree(tree: List[Path]) -> List[Path]:
    for path in tree:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("")
    return tree


async def test_scenario_file_finder(tmp_path: Path):
    tree = _create_file_tree([
        (tmp_path / ".DS_Store"),
        (tmp_path / "scenario1.py"),
        (tmp_path / "scenario2.py"),
        (tmp_path / "folder1" / "scenario3.py"),
        (tmp_path / "folder1" / "__pycache__" / "scenario3.pyc"),
        (tmp_path / "folder2" / "__init__.py"),
        (tmp_path / "folder2" / "scenario4.py"),
        (tmp_path / "folder2" / "scenario5.py"),
        (tmp_path / "folder3" / "folder4" / "scenario6.py"),
        (tmp_path / "folder3" / "folder4" / "scenario6.pyc"),
    ])

    finder = ScenarioFileFinder()
    paths = []
    async for path in finder.find(tmp_path):
        paths.append(path)

    assert set(paths) == set(tree)
    assert len(paths) == len(tree)


async def test_scenario_file_finder_with_file_filter(tmp_path: Path):
    subtree = [
        (tmp_path / "scenario1.py"),
        (tmp_path / "scenario2.py"),
        (tmp_path / ".folder1" / "scenario3.py"),
    ]
    _create_file_tree(subtree + [
        (tmp_path / ".DS_Store"),
        (tmp_path / ".folder1" / ".DS_Store"),
    ])

    finder = ScenarioFileFinder(file_filter=HiddenFilter())
    paths = []
    async for path in finder.find(tmp_path):
        paths.append(path)

    assert set(paths) == set(subtree)
    assert len(paths) == len(subtree)


async def test_scenario_file_finder_with_dir_filter(tmp_path: Path):
    subtree = [
        (tmp_path / "scenario1.py"),
        (tmp_path / "folder1" / "scenario3.py"),
        (tmp_path / "folder2" / "__init__.py"),
    ]
    _create_file_tree(subtree + [
        (tmp_path / "folder1" / "__pycache__" / "scenario3.pyc"),
    ])

    finder = ScenarioFileFinder(dir_filter=DunderFilter())
    paths = []
    async for path in finder.find(tmp_path):
        paths.append(path)

    assert set(paths) == set(subtree)
    assert len(paths) == len(subtree)
