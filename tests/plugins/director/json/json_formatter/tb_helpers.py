import importlib.util
import sys
from os import linesep
from pathlib import Path
from types import ModuleType
from typing import List, Tuple, Type

from vedro.core import ExcInfo
from vedro import create_tmp_dir

__all__ = ("create_call_stack", "run_module_function",)

FrameInfo = Tuple[str, str]  # (file_path, function_name)


def create_call_stack(frames: List[FrameInfo], *,
                      import_statement: str = "",
                      call_statement: str = "1 / 0") -> Path:
    root_dir = create_tmp_dir()

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

    return root_dir


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
                        catch: Type[Exception] = ZeroDivisionError) -> ExcInfo:
    module = import_module(str(module_path))
    try:
        getattr(module, func)()
    except catch:
        exc_type, exc_value, exc_tb  = sys.exc_info()
        return ExcInfo(exc_type, exc_value, exc_tb)
    else:
        raise RuntimeError(f"Function '{func}' in module '{module_path}' did not raise '{catch}'")
