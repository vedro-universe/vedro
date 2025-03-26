import tempfile
from pathlib import Path
from typing import Optional

__all__ = ("TempFileManager",)


class TempFileManager:
    """
    Manager for handling temporary files and directories in a project environment.

    This class provides functionalities to create and manage temporary files and directories.
    It ensures that these temporary resources are organized within the project's directory
    structure, specifically under a '.vedro/tmp' subdirectory. This allows for easy management
    and cleanup of temporary resources created during the project's lifecycle.
    """

    def __init__(self, project_dir: Path = Path.cwd()) -> None:
        """
        Initialize the TempFileManager with a specific project directory.

        :param project_dir: The root directory of the project. Defaults to the current
        working directory.
        """
        self._project_dir = project_dir.resolve()
        # default project_dir will be removed in v2.0
        self._tmp_root = self._project_dir / ".vedro" / "tmp/"

    def get_project_dir(self) -> Path:
        """
        Get the project directory associated with this manager.

        :return: A Path object representing the project directory.
        """
        return self._project_dir

    def set_project_dir(self, project_dir: Path) -> None:
        """
        Set the project directory associated with this manager.

        :param project_dir: The root directory of the project.
        """
        self._project_dir = project_dir

    def get_tmp_root(self) -> Path:
        """
        Get the root directory where temporary files and directories are stored.

        :return: A Path object representing the root temporary directory.
        """
        return self._tmp_root

    def set_tmp_root(self, tmp_root: Path) -> None:
        """
        Set the root directory for temporary files and directories.

        :param tmp_root: A path to use as the root temporary directory.
        """
        self._tmp_root = tmp_root

    def create_tmp_dir(self, *,
                       suffix: Optional[str] = None, prefix: Optional[str] = None) -> Path:
        """
        Create a temporary directory within a specified root directory.

        The dir is created in the '.vedro/tmp' directory within the current working directory.
        It has a unique name, which can be customized with an optional suffix and prefix.

        :param suffix: An optional suffix to append to the temporary directory's name.
        :param prefix: An optional prefix to prepend to the temporary directory's name.
        :return: A Path object representing the path to the created temporary directory.
        """
        tmp_root = self.get_tmp_root()
        tmp_root.mkdir(parents=True, exist_ok=True)
        tmp_dir = tempfile.mkdtemp(dir=str(tmp_root), suffix=suffix, prefix=prefix)
        return Path(tmp_dir)

    def create_tmp_file(self, *,
                        suffix: Optional[str] = None, prefix: Optional[str] = None) -> Path:
        """
        Create a temporary file within a specified root directory.

        The file is created in the '.vedro/tmp' directory within the current working directory.
        It has a unique name, which can be customized with an optional suffix and prefix.

        :param suffix: An optional suffix to append to the temporary file's name.
        :param prefix: An optional prefix to prepend to the temporary file's name.
        :return: A Path object representing the path to the created temporary file.
        """
        tmp_root = self.get_tmp_root()
        tmp_root.mkdir(parents=True, exist_ok=True)
        tmp_file = tempfile.NamedTemporaryFile(dir=str(tmp_root), suffix=suffix, prefix=prefix,
                                               delete=False)
        tmp_file.close()
        return Path(tmp_file.name)
