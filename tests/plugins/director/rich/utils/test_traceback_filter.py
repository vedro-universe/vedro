import json
from inspect import getfile
from os.path import abspath
from pathlib import Path

import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro.plugins.director.rich.utils import TracebackFilter

from ._utils import create_call_stack, get_frames_info, run_module_function, tmp_dir

__all__ = ("tmp_dir",)  # pytest fixtures


def test_no_modules(tmp_dir: Path):
    with given:
        create_call_stack(tmp_dir, [
            ("main.py", "main"),
            ("some_module/caller.py", "call_another"),
            ("another_module/__main__.py", "do_smth"),
        ])
        tb = run_module_function(tmp_dir / "main.py", func="main")

    with when:
        filtered_tb = TracebackFilter(modules=[]).filter_tb(tb)

    with then:
        assert get_frames_info(filtered_tb) == [
            (getfile(run_module_function), "run_module_function"),
            (abspath("main.py"), "main"),
            (abspath("some_module/caller.py"), "call_another"),
            (abspath("another_module/__main__.py"), "do_smth"),
        ]


def test_exclude_last_module(tmp_dir: Path):
    with given:
        create_call_stack(tmp_dir, [
            ("main.py", "main"),
            ("some_module/caller.py", "call_another"),
            ("another_module/__main__.py", "call_nested"),
            ("another_module/nested.py", "do_smth"),
        ])
        tb = run_module_function(tmp_dir / "main.py", func="main")

    with when:
        filtered_tb = TracebackFilter(modules=["another_module/nested.py"]).filter_tb(tb)

    with then:
        assert get_frames_info(filtered_tb) == [
            (getfile(run_module_function), "run_module_function"),
            (abspath("main.py"), "main"),
            (abspath("some_module/caller.py"), "call_another"),
            (abspath("another_module/__main__.py"), "call_nested"),
        ]


def test_exclude_first_module(tmp_dir: Path):
    with given:
        create_call_stack(tmp_dir, [
            ("main.py", "main"),
            ("some_module/caller.py", "call_another"),
            ("another_module/__main__.py", "call_nested"),
            ("another_module/nested.py", "do_smth"),
        ])
        tb = run_module_function(tmp_dir / "main.py", func="main")

    with when:
        filtered_tb = TracebackFilter(modules=[getfile(run_module_function)]).filter_tb(tb)

    with then:
        assert get_frames_info(filtered_tb) == [
            (abspath("main.py"), "main"),
            (abspath("some_module/caller.py"), "call_another"),
            (abspath("another_module/__main__.py"), "call_nested"),
            (abspath("another_module/nested.py"), "do_smth"),
        ]


def test_exclude_multiple_modules(tmp_dir: Path):
    with given:
        create_call_stack(tmp_dir, [
            ("main.py", "main"),
            ("some_module/caller.py", "call_another"),
            ("another_module/file.py", "call_nested"),
            ("another_module/nested.py", "do_smth"),
        ])
        tb = run_module_function(tmp_dir / "main.py", func="main")

        modules = ["another_module/file.py", "another_module/nested.py"]

    with when:
        filtered_tb = TracebackFilter(modules).filter_tb(tb)

    with then:
        assert get_frames_info(filtered_tb) == [
            (getfile(run_module_function), "run_module_function"),
            (abspath("main.py"), "main"),
            (abspath("some_module/caller.py"), "call_another"),
        ]


def test_exclude_entire_module(tmp_dir: Path):
    with given:
        create_call_stack(tmp_dir, [
            ("main.py", "main"),
            ("some_module/caller.py", "call_another"),
            ("another_module/__main__.py", "call_nested"),
            ("another_module/nested.py", "do_smth"),
        ])
        tb = run_module_function(tmp_dir / "main.py", func="main")

    with when:
        filtered_tb = TracebackFilter(["another_module"]).filter_tb(tb)

    with then:
        assert get_frames_info(filtered_tb) == [
            (getfile(run_module_function), "run_module_function"),
            (abspath("main.py"), "main"),
            (abspath("some_module/caller.py"), "call_another"),
        ]


@pytest.mark.parametrize(("module", "resolved"), [
    # relative dir
    ("some_module", Path("some_module").resolve()),
    # relative file
    ("some_module/file.py", Path("some_module/file.py").resolve()),
    # absolute dir
    (json.__file__, Path(json.__file__)),
])
def test_resolve_path_from_string(module: str, resolved: Path):
    with given:
        traceback_filter = TracebackFilter(modules=[])

    with when:
        result = traceback_filter.resolve_module_path(module)

    with then:
        assert result == resolved


def test_resolve_path_invalid_type():
    with given:
        traceback_filter = TracebackFilter(modules=[])

    with when, raises(Exception) as exc:
        traceback_filter.resolve_module_path(None)  # type: ignore

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == "'None' must be a module or a path"
