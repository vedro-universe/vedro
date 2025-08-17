import sys
from os import linesep

from baby_steps import given, then, when
from pytest import raises

from vedro.core.output_capturer import CapturedOutput


def test_captured_output_get_value_before_capture():
    with given:
        captured = CapturedOutput()

    with when:
        result = captured.get_value()

    with then:
        assert result == ""


def test_captured_output_capture_stdout():
    with given:
        captured = CapturedOutput()
        test_message = "Hello from stdout"

    with when:
        with captured:
            print(test_message, end="")

    with then:
        assert captured.get_value() == test_message


def test_captured_output_capture_stderr():
    with given:
        captured = CapturedOutput()
        test_message = "Error from stderr"

    with when:
        with captured:
            print(test_message, file=sys.stderr, end="")

    with then:
        assert captured.get_value() == test_message


def test_captured_output_preserve_interleaved_order():
    with given:
        captured = CapturedOutput()

    with when:
        with captured:
            print("1-stdout")
            print("2-stderr", file=sys.stderr)
            print("3-stdout")
            print("4-stderr", file=sys.stderr)

    with then:
        output = captured.get_value()
        lines = output.strip().split(linesep)
        assert lines == ["1-stdout", "2-stderr", "3-stdout", "4-stderr"]


def test_captured_output_empty_capture():
    with given:
        captured = CapturedOutput()

    with when:
        with captured:
            pass  # No output

    with then:
        assert captured.get_value() == ""


def test_captured_output_with_exception_inside_context():
    with given:
        captured = CapturedOutput()
        test_message = "Before exception"

    with when, raises(ValueError):
        with captured:
            print(test_message, end="")
            raise ValueError("Test exception")

    with then:
        assert captured.get_value() == test_message


def test_captured_output_context_manager_returns_self():
    with given:
        captured = CapturedOutput()

    with when:
        with captured as ctx:
            result = ctx

    with then:
        assert result is captured


def test_captured_output_nested_contexts():
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
        assert inner_captured.get_value() == f"Inner{linesep}"
        assert outer_captured.get_value() == f"Outer 1{linesep}Outer 2{linesep}"


def test_captured_output_after_exit():
    with given:
        captured = CapturedOutput()

        with captured:
            print("Inside context")

    with when:
        print("Outside context")  # This should not be captured

    with then:
        assert captured.get_value() == f"Inside context{linesep}"
        assert "Outside context" not in captured.get_value()


def test_captured_output_reuse_same_instance():
    with given:
        captured = CapturedOutput()

        with captured:
            print("First use")

    with when:
        with captured:
            print("Second use")

    with then:
        # Both captures should be accumulated in the same buffer
        output = captured.get_value()
        assert output == f"First use{linesep}Second use{linesep}"


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
