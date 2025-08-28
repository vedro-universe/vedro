from traceback import extract_tb

from vedro import given, scenario, then, when
from vedro.core.exc_info import TracebackFilter
from ._helpers import make_json_formatter
from .tb_helpers import run_module_function, create_call_stack


@scenario
def format_exc_info():
    with given:
        tb_filter = TracebackFilter(modules=[])
        formatter = make_json_formatter(tb_filter=tb_filter)

        tmp_dir = create_call_stack([
            ("main.py", "main"),
        ])
        exc_info = run_module_function(tmp_dir / "main.py", "main")

    with when:
        formatted_exc_info = formatter.format_exc_info(exc_info)

    with then:
        last_frame = extract_tb(exc_info.traceback)[-1]
        assert formatted_exc_info == {
            "type": "ZeroDivisionError",
            "message": "division by zero",
            "file": last_frame.filename,
            "lineno": last_frame.lineno,
        }
