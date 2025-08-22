import sys

from baby_steps import given, then, when

from vedro.core.output_capturer import NoOpCapturedOutput, StreamView


def test_noop_captured_output_stdout():
    with given:
        captured_output = NoOpCapturedOutput()

    with when:
        stdout_view = captured_output.stdout

    with then:
        assert isinstance(stdout_view, StreamView)
        assert stdout_view.get_value() == ""


def test_noop_captured_output_stderr():
    with given:
        capturer = NoOpCapturedOutput()

    with when:
        stderr_view = capturer.stderr

    with then:
        assert isinstance(stderr_view, StreamView)
        assert stderr_view.get_value() == ""


def test_noop_captured_output_stdout_after_print():
    with given:
        capturer = NoOpCapturedOutput()

    with when:
        with capturer:
            print("This should not be captured")

    with then:
        assert capturer.stdout.get_value() == ""
        assert capturer.stderr.get_value() == ""


def test_noop_captured_output_stderr_after_print():
    with given:
        capturer = NoOpCapturedOutput()

    with when:
        with capturer:
            print("This should not be captured", file=sys.stderr)

    with then:
        assert capturer.stdout.get_value() == ""
        assert capturer.stderr.get_value() == ""


def test_noop_captured_output_context_manager():
    with given:
        capturer = NoOpCapturedOutput()

    with when:
        with capturer as ctx:
            result = ctx

    with then:
        assert result is capturer
