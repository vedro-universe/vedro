from pathlib import Path

from baby_steps import then, when

from vedro.plugins.temp_keeper import TempFileManager

from ._utils import temp_file_manager

__all__ = ("temp_file_manager",)  # fixtures


def test_get_project_dir(*, temp_file_manager: TempFileManager, tmp_path: Path):
    with when:
        project_dir = temp_file_manager.get_project_dir()

    with then:
        assert project_dir == tmp_path


def test_get_tmp_root(*, temp_file_manager: TempFileManager, tmp_path: Path):
    with when:
        project_dir = temp_file_manager.get_tmp_root()

    with then:
        assert project_dir == tmp_path / ".vedro" / "tmp"


def test_create_tmp_dir(*, temp_file_manager: TempFileManager, tmp_path: Path):
    with when:
        tmp_dir = temp_file_manager.create_tmp_dir()

    with then:
        assert tmp_dir.parent == tmp_path / ".vedro" / "tmp"
        assert tmp_dir.is_dir()


def test_create_tmp_file(*, temp_file_manager: TempFileManager, tmp_path: Path):
    with when:
        tmp_file = temp_file_manager.create_tmp_file()

    with then:
        assert tmp_file.parent == tmp_path / ".vedro" / "tmp"
        assert tmp_file.is_file()


def test_create_tmp_dir_prefix(*, temp_file_manager: TempFileManager):
    with when:
        tmp_dir = temp_file_manager.create_tmp_dir(prefix="banana")

    with then:
        assert tmp_dir.name.startswith("banana")


def test_create_tmp_dir_suffix(*, temp_file_manager: TempFileManager):
    with when:
        tmp_dir = temp_file_manager.create_tmp_dir(suffix="banana")

    with then:
        assert tmp_dir.name.endswith("banana")


def test_create_tmp_file_prefix(*, temp_file_manager: TempFileManager):
    with when:
        tmp_file = temp_file_manager.create_tmp_file(prefix="banana")

    with then:
        assert tmp_file.name.startswith("banana")


def test_create_tmp_file_suffix(*, temp_file_manager: TempFileManager):
    with when:
        tmp_file = temp_file_manager.create_tmp_file(suffix="banana")

    with then:
        assert tmp_file.name.endswith("banana")
