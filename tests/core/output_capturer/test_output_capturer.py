from baby_steps import given, then, when

from vedro.core.output_capturer import CapturedOutput, OutputCapturer
from vedro.core.output_capturer._output_capturer import NoOpCapturedOutput


def test_output_capturer_initialization_defaults():
    with when:
        capturer = OutputCapturer()

    with then:
        assert capturer.enabled is False
        assert capturer.capture_limit is None


def test_output_capturer_initialization_enabled_with_limit():
    with given:
        enabled = True
        capture_limit = 50

    with when:
        capturer = OutputCapturer(enabled=enabled, capture_limit=capture_limit)

    with then:
        assert capturer.enabled is True
        assert capturer.capture_limit == capture_limit


def test_output_capturer_capture_when_disabled():
    with given:
        capturer = OutputCapturer(enabled=False)

    with when:
        captured = capturer.capture()

    with then:
        assert isinstance(captured, NoOpCapturedOutput)


def test_output_capturer_capture_when_enabled():
    with given:
        capturer = OutputCapturer(enabled=True)

    with when:
        captured = capturer.capture()

    with then:
        assert isinstance(captured, CapturedOutput)
        assert not isinstance(captured, NoOpCapturedOutput)


def test_noop_captured_output_get_value():
    with given:
        capturer = NoOpCapturedOutput()

    with when:
        value = capturer.get_value()

    with then:
        assert value == ""


def test_noop_captured_output_get_value_after_print():
    with given:
        capturer = NoOpCapturedOutput()

    with when:
        with capturer:
            print("This should not be captured")

    with then:
        assert capturer.get_value() == ""


def test_noop_captured_output_context_manager():
    with given:
        capturer = NoOpCapturedOutput()

    with when:
        with capturer as ctx:
            result = ctx

    with then:
        assert result is capturer
