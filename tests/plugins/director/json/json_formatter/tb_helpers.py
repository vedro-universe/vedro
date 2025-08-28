import importlib.util
import sys
from os import linesep
from pathlib import Path
from types import ModuleType
from typing import List, Tuple, Type

from vedro import create_tmp_dir

__all__ = ("generate_call_chain_modules", "execute_and_capture_exception",)

from vedro.core import ExcInfo

FrameInfo = Tuple[str, str]  # (file_path, function_name)


def generate_call_chain_modules(frames: List[FrameInfo], *,
                                import_statement: str = "",
                                call_statement: str = "1 / 0") -> Path:
    """
    Generate a chain of Python modules that call each other in sequence.

    This function generates a series of Python files that call each other in sequence,
    creating a specific call stack structure. Each frame in the stack represents a
    function in a module that calls the next function in the chain.

    :param frames: A list of (file_path, function_name) tuples defining the call stack.
                   Each tuple represents one frame in the stack, where file_path is
                   relative to the temporary directory and function_name is the name
                   of the function to create.
    :param import_statement: Optional import statement to include in the last file.
                             Defaults to an empty string.
    :param call_statement: The statement to execute in the last function of the stack.
                           Defaults to "1 / 0" to raise a ZeroDivisionError.
    :return: Path to the root directory containing the generated module structure.
    """
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
            module_name = filepath_to_module_name(Path(next_file_path))
            import_stmt = f"from {module_name} import {next_function_name}"
            call_stmt = f"  {next_function_name}()"

        if not file_path.parent.exists():
            file_path.parent.mkdir(parents=True)
            (file_path.parent / "__init__.py").touch()

        file_path.write_text(linesep.join([import_stmt, func_declaration, call_stmt]))

    return root_dir


def filepath_to_module_name(path: Path) -> str:
    """
    Convert a file path to a Python module name.

    :param path: The file path to convert.
    :return: The module name as a dotted string (e.g., "package.subpackage.module").
    """
    return ".".join(path.with_suffix("").parts)


def load_module_from_path(path: str) -> ModuleType:
    """
    Load a Python module from a file path dynamically.

    :param path: The path to the Python file or directory (with __init__.py).
    :return: The loaded module object.
    """
    path = Path(path).absolute().relative_to(Path.cwd())

    if path.is_dir():
        path /= "__init__.py"

    module_name = filepath_to_module_name(path)

    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def execute_and_capture_exception(module_path: Path, func: str,
                                  catch: Type[Exception] = ZeroDivisionError) -> ExcInfo:
    """
    Execute a function from a module and capture its exception information.

    This function imports a module from the given path, executes the specified
    function, and captures the exception information if the expected exception
    is raised.

    :param module_path: Path to the Python module file to import.
    :param func: Name of the function to execute from the module.
    :param catch: The exception type to catch. Defaults to ZeroDivisionError.
    :return: ExcInfo object containing the exception type, value, and traceback.
    :raises RuntimeError: If the function does not raise the expected exception.
    """
    module = load_module_from_path(str(module_path))
    try:
        getattr(module, func)()
    except catch:
        exc_type, exc_value, exc_tb = sys.exc_info()
        return ExcInfo(exc_type, exc_value, exc_tb)
    else:
        raise RuntimeError(f"Function '{func}' in module '{module_path}' did not raise '{catch}'")
