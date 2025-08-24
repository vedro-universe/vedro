import sys
from os import linesep

from baby_steps import given, then, when
from pytest import raises

from vedro.core.output_capturer import CapturedOutput, StreamView


def test_captured_output_stdout():
    with given:
        captured = CapturedOutput()

    with when:
        stdout_view = captured.stdout

    with then:
        assert isinstance(stdout_view, StreamView)


def test_captured_output_stderr():
    with given:
        captured = CapturedOutput()

    with when:
        stderr_view = captured.stderr

    with then:
        assert isinstance(stderr_view, StreamView)


def test_captured_output_capture_stdout():
    with given:
        captured = CapturedOutput()
        test_message = "Hello from stdout"

    with when:
        with captured:
            print(test_message, end="")

    with then:
        assert captured.stdout.get_value() == test_message
        assert captured.stderr.get_value() == ""


def test_captured_output_capture_stderr():
    with given:
        captured = CapturedOutput()
        test_message = "Error from stderr"

    with when:
        with captured:
            print(test_message, file=sys.stderr, end="")

    with then:
        assert captured.stdout.get_value() == ""
        assert captured.stderr.get_value() == test_message


def test_captured_output_separate_streams():
    with given:
        captured = CapturedOutput()

    with when:
        with captured:
            print("1-stdout")
            print("2-stderr", file=sys.stderr)
            print("3-stdout")
            print("4-stderr", file=sys.stderr)

    with then:
        stdout_output = captured.stdout.get_value()
        stderr_output = captured.stderr.get_value()

        stdout_lines = stdout_output.strip().split(linesep)
        stderr_lines = stderr_output.strip().split(linesep)

        assert stdout_lines == ["1-stdout", "3-stdout"]
        assert stderr_lines == ["2-stderr", "4-stderr"]


def test_captured_output_empty_capture():
    with given:
        captured = CapturedOutput()

    with when:
        with captured:
            pass  # No output

    with then:
        assert captured.stdout.get_value() == ""
        assert captured.stderr.get_value() == ""


def test_captured_output_context_manager_returns_self():
    with given:
        captured = CapturedOutput()

    with when:
        with captured as ctx:
            result = ctx

    with then:
        assert result is captured


def test_captured_output_stdout_with_exception_inside_context():
    with given:
        captured = CapturedOutput()
        stdout_message = "Before exception stdout"

    with when, raises(ValueError):
        with captured:
            print(stdout_message, end="")
            raise ValueError("Test exception")

    with then:
        assert captured.stdout.get_value() == stdout_message
        assert captured.stderr.get_value() == ""


def test_captured_output_stderr_with_exception_inside_context():
    with given:
        captured = CapturedOutput()
        stderr_message = "Before exception stderr"

    with when, raises(ValueError):
        with captured:
            print(stderr_message, file=sys.stderr, end="")
            raise ValueError("Test exception")

    with then:
        assert captured.stdout.get_value() == ""
        assert captured.stderr.get_value() == stderr_message


def test_captured_output_stdout_nested_contexts():
    with given:
        outer_captured = CapturedOutput()
        inner_captured = CapturedOutput()

    with when:
        with outer_captured:
            print("Outer 1")
            with inner_captured:
                print("Inner")
            print("Outer 2")

    with then:
        assert inner_captured.stdout.get_value() == f"Inner{linesep}"
        assert outer_captured.stdout.get_value() == f"Outer 1{linesep}Outer 2{linesep}"

        assert outer_captured.stderr.get_value() == ""


def test_captured_output_stderr_nested_contexts():
    with given:
        outer_captured = CapturedOutput()
        inner_captured = CapturedOutput()

    with when:
        with outer_captured:
            print("Outer 1", file=sys.stderr)
            with inner_captured:
                print("Inner", file=sys.stderr)
            print("Outer 2", file=sys.stderr)

    with then:
        assert inner_captured.stderr.get_value() == f"Inner{linesep}"
        assert outer_captured.stderr.get_value() == f"Outer 1{linesep}Outer 2{linesep}"

        assert outer_captured.stdout.get_value() == ""


def test_captured_output_stdout_after_exit():
    with given:
        captured = CapturedOutput()

        with captured:
            print("Inside context stdout")

    with when:
        print("Outside context stdout")  # This should not be captured

    with then:
        assert captured.stdout.get_value() == f"Inside context stdout{linesep}"
        assert captured.stderr.get_value() == ""


def test_captured_output_stderr_after_exit():
    with given:
        captured = CapturedOutput()

        with captured:
            print("Inside context stderr", file=sys.stderr)

    with when:
        print("Outside context stderr", file=sys.stderr)  # This should not be captured

    with then:
        assert captured.stderr.get_value() == f"Inside context stderr{linesep}"
        assert captured.stdout.get_value() == ""


def test_captured_output_reuse_same_instance():
    with given:
        captured = CapturedOutput()

        with captured:
            print("First use stdout")
            print("First use stderr", file=sys.stderr)

    with when:
        with captured:
            print("Second use stdout")
            print("Second use stderr", file=sys.stderr)

    with then:
        stdout_output = captured.stdout.get_value()
        assert stdout_output == f"First use stdout{linesep}Second use stdout{linesep}"

        stderr_output = captured.stderr.get_value()
        assert stderr_output == f"First use stderr{linesep}Second use stderr{linesep}"


def test_captured_output_exit_restores_streams():
    with given:
        captured = CapturedOutput()
        original_stdout = sys.stdout
        original_stderr = sys.stderr

    with when:
        with captured:
            inside_stdout, inside_stderr = sys.stdout, sys.stderr

    with then:
        # Inside context, streams should be redirected
        assert inside_stdout != original_stdout
        assert inside_stderr != original_stderr

        # After context, streams should be restored
        assert sys.stdout == original_stdout
        assert sys.stderr == original_stderr
