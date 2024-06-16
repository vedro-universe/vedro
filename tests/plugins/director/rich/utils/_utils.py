import importlib.util
import os
import sys
import traceback
from os import linesep
from os.path import abspath
from pathlib import Path
from types import ModuleType, TracebackType
from typing import List, Tuple, Type

import pytest

__all__ = ("create_call_stack", "run_module_function", "import_module", "get_frames_info",
           "tmp_dir",)


FrameInfo = Tuple[str, str]  # (file_path, function_name)


def create_call_stack(root_dir: Path, frames: List[FrameInfo], *,
                      import_statement: str = "",
                      call_statement: str = "1 / 0") -> None:
    """
    Create a call stack of Python functions based on provided frame information.

    :param root_dir: The root directory where the files should be created.
    :param frames: A list of tuples, each containing a file path and function name.
    :param import_statement: The import statement to include in the last frame file.
    :param call_statement: The call statement to include in the last frame file.
    """
    for index, frame in enumerate(frames):
        file_path, function_name = frame
        file_path = (root_dir / file_path).resolve()

        func_declaration = f"def {function_name}():"
        if index == len(frames) - 1:
            import_stmt = import_statement
            call_stmt = f"  {call_statement}"
        else:
            next_file_path, next_function_name = frames[index + 1]
            module_name = path_to_module(Path(next_file_path))
            import_stmt = f"from {module_name} import {next_function_name}"
            call_stmt = f"  {next_function_name}()"

        if not file_path.parent.exists():
            file_path.parent.mkdir(parents=True)
            (file_path.parent / "__init__.py").touch()

        file_path.write_text(linesep.join([import_stmt, func_declaration, call_stmt]))


def path_to_module(path: Path) -> str:
    """
    Convert a file path to a Python module path.

    :param path: The path to convert.
    :return: The module path as a string.
    """
    return ".".join(path.with_suffix("").parts)


def import_module(path: str) -> ModuleType:
    """
    Import a Python module from a given file path.

    :param path: The path to the Python file.
    :return: The imported module.
    """
    path = Path(path).absolute().relative_to(Path.cwd())

    if path.is_dir():
        path /= "__init__.py"

    module_name = path_to_module(path)

    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def run_module_function(module_path: Path, func: str,
                        catch: Type[Exception] = ZeroDivisionError) -> TracebackType:
    """
    Run a specified function from a module, catching and returning the traceback on exception.

    :param module_path: The path to the module file.
    :param func: The function name to execute. Defaults to 'main'.
    :param catch: The exception type to catch. Defaults to 'ZeroDivisionError'.
    :return: The traceback object if an exception is raised.
    """
    module = import_module(str(module_path))
    try:
        getattr(module, func)()
    except catch:
        *_, tb = sys.exc_info()
        return tb


def get_frames_info(tb: TracebackType) -> List[FrameInfo]:
    """
    Extract frame information from a traceback object.

    :param tb: The traceback object.
    :return: A list of tuples containing file paths and function names from the traceback.
    """
    frames_info = []
    for frame in traceback.extract_tb(tb):
        filename = frame.filename
        if sys.version_info < (3, 10):
            filename = abspath(filename)
        frames_info.append((filename, frame.name))
    return frames_info


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    """
    Create a temporary directory fixture for testing purposes.

    This fixture changes the current working directory to a temporary path,
    adds this path to `sys.path`, and ensures that the original directory and
    path settings are restored after the test completes.

    :param tmp_path: The temporary path provided by the pytest fixture.
    :return: The temporary path used during the test.
    """
    cwd = os.getcwd()
    modules = set(sys.modules.keys())
    try:
        os.chdir(tmp_path)
        sys.path.append(str(tmp_path))
        yield tmp_path
    finally:
        sys.path.remove(str(tmp_path))
        os.chdir(cwd)
        new_modules = set(sys.modules.keys()) - modules
        for module in new_modules:
            del sys.modules[module]
