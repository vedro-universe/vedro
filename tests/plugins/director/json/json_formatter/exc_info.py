from traceback import extract_tb

from vedro import given, scenario, then, when
from vedro.core.exc_info import TracebackFilter

from ._helpers import make_json_formatter
from .tb_helpers import execute_and_capture_exception, generate_call_chain_modules


@scenario
def format_exc_info():
    with given:
        tb_filter = TracebackFilter(modules=[])
        formatter = make_json_formatter(tb_filter=tb_filter)

        tmp_dir = generate_call_chain_modules([("main.py", "main")])
        exc_info = execute_and_capture_exception(tmp_dir / "main.py", "main")

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
