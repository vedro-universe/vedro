from rich.traceback import Trace

__all__ = ("filter_locals",)


def filter_locals(trace: Trace) -> None:
    for stack in trace.stacks:
        for frame in stack.frames:
            if frame.locals is not None:
                frame.locals = {k: v for k, v in frame.locals.items()
                                if k != "self" and k.isidentifier()}
