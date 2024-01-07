import os
from types import FrameType, TracebackType
from typing import Optional, cast

import vedro

__all__ = ("filter_internals",)


def filter_internals(traceback: TracebackType) -> TracebackType:
    class _Traceback:
        def __init__(self,
                     tb_frame: FrameType,
                     tb_lasti: int,
                     tb_lineno: int,
                     tb_next: Optional[TracebackType]) -> None:
            self.tb_frame = tb_frame
            self.tb_lasti = tb_lasti
            self.tb_lineno = tb_lineno
            self.tb_next = tb_next

    tb = _Traceback(traceback.tb_frame, traceback.tb_lasti, traceback.tb_lineno,
                    traceback.tb_next)

    root = os.path.dirname(vedro.__file__)
    while tb.tb_next is not None:
        filename = os.path.abspath(tb.tb_frame.f_code.co_filename)
        if os.path.commonpath([root, filename]) != root:
            break
        tb = tb.tb_next  # type: ignore

    return cast(TracebackType, tb)
