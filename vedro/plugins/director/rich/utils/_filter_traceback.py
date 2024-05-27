import os
from pathlib import Path
from types import TracebackType
from typing import List

__all__ = ("filter_traceback",)


def filter_traceback(tb: TracebackType, modules: List[str]) -> TracebackType:
    modules = [os.path.abspath(module) for module in modules]

    filtered_tb = None
    last_tb = None

    while tb is not None:
        filename = Path(tb.tb_frame.f_code.co_filename)

        if not any(filename.is_relative_to(module) for module in modules):
            # Create a new traceback object if it is not a filtered file
            if last_tb is None:
                # Create a new 'root' traceback
                filtered_tb = tb
                last_tb = tb
            else:
                # Append the current traceback to the last valid traceback
                last_tb.tb_next = tb
                last_tb = tb

        # Move to the next traceback object
        tb = tb.tb_next  # type: ignore

    # Ensure the last traceback in the chain doesn't link to excluded frames
    if last_tb is not None:
        last_tb.tb_next = None

    return filtered_tb
