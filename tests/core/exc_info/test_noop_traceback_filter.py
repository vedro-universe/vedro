from inspect import getfile
from os.path import abspath
from pathlib import Path

from baby_steps import given, then, when

from vedro.core.exc_info import NoOpTracebackFilter

from ._utils import create_call_stack, get_frames_info, run_module_function, tmp_dir

__all__ = ("tmp_dir",)  # pytest fixtures


def test_noop_filter_preserves_all_frames(tmp_dir: Path):
    with given:
        create_call_stack(tmp_dir, [
            ("main.py", "main"),
            ("some_module/caller.py", "call_another"),
            ("another_module/__main__.py", "call_nested"),
            ("another_module/nested.py", "do_smth"),
        ])
        tb = run_module_function(tmp_dir / "main.py", func="main")
        original_frames = get_frames_info(tb)

    with when:
        no_op_filter = NoOpTracebackFilter(modules=[])
        filtered_tb = no_op_filter.filter_tb(tb)

    with then:
        assert get_frames_info(filtered_tb) == original_frames
        assert get_frames_info(filtered_tb) == [
            (getfile(run_module_function), "run_module_function"),
            (abspath("main.py"), "main"),
            (abspath("some_module/caller.py"), "call_another"),
            (abspath("another_module/__main__.py"), "call_nested"),
            (abspath("another_module/nested.py"), "do_smth"),
        ]


def test_noop_filter_ignores_modules_parameter(tmp_dir: Path):
    with given:
        create_call_stack(tmp_dir, [
            ("main.py", "main"),
            ("some_module/caller.py", "call_another"),
            ("another_module/file.py", "call_nested"),
            ("another_module/nested.py", "do_smth"),
        ])
        tb = run_module_function(tmp_dir / "main.py", func="main")
        modules_to_filter = ["another_module/file.py", "another_module/nested.py"]

    with when:
        no_op_filter = NoOpTracebackFilter(modules=modules_to_filter)
        filtered_tb = no_op_filter.filter_tb(tb)

    with then:
        assert get_frames_info(filtered_tb) == [
            (getfile(run_module_function), "run_module_function"),
            (abspath("main.py"), "main"),
            (abspath("some_module/caller.py"), "call_another"),
            (abspath("another_module/file.py"), "call_nested"),
            (abspath("another_module/nested.py"), "do_smth"),
        ]


def test_noop_filter_with_entire_module_in_filter_list(tmp_dir: Path):
    with given:
        create_call_stack(tmp_dir, [
            ("main.py", "main"),
            ("some_module/caller.py", "call_another"),
            ("another_module/__main__.py", "call_nested"),
            ("another_module/nested.py", "do_smth"),
        ])
        tb = run_module_function(tmp_dir / "main.py", func="main")

    with when:
        no_op_filter = NoOpTracebackFilter(modules=["another_module"])
        filtered_tb = no_op_filter.filter_tb(tb)

    with then:
        assert get_frames_info(filtered_tb) == [
            (getfile(run_module_function), "run_module_function"),
            (abspath("main.py"), "main"),
            (abspath("some_module/caller.py"), "call_another"),
            (abspath("another_module/__main__.py"), "call_nested"),
            (abspath("another_module/nested.py"), "do_smth"),
        ]
