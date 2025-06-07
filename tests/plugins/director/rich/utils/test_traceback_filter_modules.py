import json
import sys
from inspect import getfile
from json.decoder import JSONDecodeError
from os.path import abspath, dirname
from pathlib import Path

from baby_steps import given, then, when
from pytest import raises

from vedro.plugins.director.rich.utils import TracebackFilter

from ._utils import create_call_stack, get_frames_info, run_module_function, tmp_dir

__all__ = ("tmp_dir",)  # pytest fixtures


def test_no_modules(tmp_dir: Path):
    with given:
        create_call_stack(tmp_dir, [("main.py", "main")],
                          import_statement="import json",
                          call_statement="json.loads('...')")
        tb = run_module_function(tmp_dir / "main.py", func="main", catch=JSONDecodeError)

    with when:
        filtered_tb = TracebackFilter(modules=[]).filter_tb(tb)

    with then:
        json_module = dirname(getfile(json))

        assert get_frames_info(filtered_tb) == [
            (getfile(run_module_function), "run_module_function"),
            (abspath("main.py"), "main"),
            (f"{json_module}/__init__.py", "loads"),
            (f"{json_module}/decoder.py", "decode"),
            (f"{json_module}/decoder.py", "raw_decode"),
        ]


def test_exclude_module(tmp_dir: Path):
    with given:
        create_call_stack(tmp_dir, [("main.py", "main")],
                          import_statement="import json",
                          call_statement="json.loads('...')")
        tb = run_module_function(tmp_dir / "main.py", func="main", catch=JSONDecodeError)

    with when:
        filtered_tb = TracebackFilter(modules=[json]).filter_tb(tb)

    with then:
        assert get_frames_info(filtered_tb) == [
            (getfile(run_module_function), "run_module_function"),
            (abspath("main.py"), "main"),
        ]


def test_resolve_path_from_module():
    with given:
        traceback_filter = TracebackFilter(modules=[])

    with when:
        result = traceback_filter.resolve_module_path(json)

    with then:
        assert result == Path(json.__file__).parent


def test_resolve_path_missing_file_attr():
    with given:
        traceback_filter = TracebackFilter(modules=[])

    with when, raises(BaseException) as exc:
        traceback_filter.resolve_module_path(sys)

    with then:
        assert exc.type is AttributeError
        assert str(exc.value) == "'sys' must be a module with a '__file__' attribute"
