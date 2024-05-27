from inspect import getfile
from os.path import abspath
from pathlib import Path

from baby_steps import given, when

from vedro.plugins.director.rich.utils import filter_traceback

from ._utils import create_call_stack, get_frames_info, run_module_function, tmp_dir

__all__ = ("tmp_dir",)  # pytest fixtures


def test_no_modules(tmp_dir: Path):
    with given:
        create_call_stack(tmp_dir, [
            ("main.py", "main"),
            ("some_module/caller.py", "call_another"),
            ("another_module/file.py", "call_nested"),
            ("another_module/nested.py", "do_smth"),
        ])
        tb = run_module_function(tmp_dir / "main.py", func="main")

    with when:
        filtered_tb = filter_traceback(tb, modules=[])

    assert get_frames_info(filtered_tb) == [
        (getfile(run_module_function), "run_module_function"),
        (abspath("main.py"), "main"),
        (abspath("some_module/caller.py"), "call_another"),
        (abspath("another_module/file.py"), "call_nested"),
        (abspath("another_module/nested.py"), "do_smth"),
    ]


def test_exclude_last_module(tmp_dir: Path):
    with given:
        create_call_stack(tmp_dir, [
            ("main.py", "main"),
            ("some_module/caller.py", "call_another"),
            ("another_module/file.py", "call_nested"),
            ("another_module/nested.py", "do_smth"),
        ])
        tb = run_module_function(tmp_dir / "main.py", func="main")

    with when:
        filtered_tb = filter_traceback(tb, modules=["another_module/nested.py"])

    assert get_frames_info(filtered_tb) == [
        (getfile(run_module_function), "run_module_function"),
        (abspath("main.py"), "main"),
        (abspath("some_module/caller.py"), "call_another"),
        (abspath("another_module/file.py"), "call_nested"),
    ]


def test_exclude_first_module(tmp_dir: Path):
    with given:
        create_call_stack(tmp_dir, [
            ("main.py", "main"),
            ("some_module/caller.py", "call_another"),
            ("another_module/file.py", "call_nested"),
            ("another_module/nested.py", "do_smth"),
        ])
        tb = run_module_function(tmp_dir / "main.py", func="main")

    with when:
        filtered_tb = filter_traceback(tb, modules=[getfile(run_module_function)])

    assert get_frames_info(filtered_tb) == [
        (abspath("main.py"), "main"),
        (abspath("some_module/caller.py"), "call_another"),
        (abspath("another_module/file.py"), "call_nested"),
        (abspath("another_module/nested.py"), "do_smth"),
    ]


def test_exclude_middle_module(tmp_dir: Path):
    with given:
        create_call_stack(tmp_dir, [
            ("main.py", "main"),
            ("some_module/caller.py", "call_another"),
            ("another_module/file.py", "call_nested"),
            ("another_module/nested.py", "do_smth"),
        ])
        tb = run_module_function(tmp_dir / "main.py", func="main")

    with when:
        filtered_tb = filter_traceback(tb, modules=["another_module/file.py"])

    assert get_frames_info(filtered_tb) == [
        (getfile(run_module_function), "run_module_function"),
        (abspath("main.py"), "main"),
        (abspath("some_module/caller.py"), "call_another"),
        (abspath("another_module/nested.py"), "do_smth"),
    ]


def test_exclude_entire_module(tmp_dir: Path):
    with given:
        create_call_stack(tmp_dir, [
            ("main.py", "main"),
            ("some_module/caller.py", "call_another"),
            ("another_module/file.py", "call_nested"),
            ("another_module/nested.py", "do_smth"),
        ])
        tb = run_module_function(tmp_dir / "main.py", func="main")

    with when:
        filtered_tb = filter_traceback(tb, modules=["another_module"])

    assert get_frames_info(filtered_tb) == [
        (getfile(run_module_function), "run_module_function"),
        (abspath("main.py"), "main"),
        (abspath("some_module/caller.py"), "call_another"),
    ]
