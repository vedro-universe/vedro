from baby_steps import given, then, when

from vedro.plugins.functioner._step_recorder import StepRecorder, get_step_recorder


def test_initial_state():
    with given:
        recorder = StepRecorder()

    with when:
        records_count = len(recorder)

    with then:
        assert records_count == 0
        assert list(recorder) == []


def test_record_without_exception():
    with given:
        recorder = StepRecorder()
        kind = "given"
        name = "test step"
        start_at = 1.0
        ended_at = 2.0

    with when:
        recorder.record(kind, name, start_at, ended_at)

    with then:
        assert len(recorder) == 1
        assert list(recorder) == [(kind, name, start_at, ended_at, None)]


def test_record_with_exception():
    with given:
        recorder = StepRecorder()
        kind = "when"
        name = "failing step"
        start_at = 1.0
        ended_at = 2.0
        exception = ValueError("test error")

    with when:
        recorder.record(kind, name, start_at, ended_at, exc=exception)

    with then:
        assert len(recorder) == 1
        assert list(recorder) == [(kind, name, start_at, ended_at, exception)]


def test_multiple_records():
    with given:
        recorder = StepRecorder()
        records = [
            ("given", "setup", 1.0, 2.0, None),
            ("when", "action", 2.0, 3.0, None),
            ("then", "verify", 3.0, 4.0, ValueError("failed")),
        ]

    with when:
        for kind, name, start, end, exc in records:
            recorder.record(kind, name, start, end, exc)

    with then:
        assert len(recorder) == 3
        assert list(recorder) == records


def test_clear():
    with given:
        recorder = StepRecorder()
        recorder.record("given", "step1", 1.0, 2.0)
        recorder.record("when", "step2", 2.0, 3.0)
        assert len(recorder) == 2

    with when:
        recorder.clear()

    with then:
        assert len(recorder) == 0
        assert list(recorder) == []


def test_iteration():
    with given:
        recorder = StepRecorder()
        records = [
            ("given", "step1", 1.0, 2.0, None),
            ("when", "step2", 2.0, 3.0, None),
        ]
        for kind, name, start, end, exc in records:
            recorder.record(kind, name, start, end, exc)

    with when:
        collected_records = [record for record in recorder]

    with then:
        assert collected_records == records


def test_singleton_pattern():
    with given:
        pass

    with when:
        recorder1 = get_step_recorder()
        recorder2 = get_step_recorder()

    with then:
        assert recorder1 is recorder2


def test_returns_step_recorder_instance():
    with given:
        pass

    with when:
        recorder = get_step_recorder()

    with then:
        assert isinstance(recorder, StepRecorder)
