from baby_steps import given, then, when

from vedro.plugins.director import Director, DirectorInitEvent, DirectorPlugin


def test_director_init_event_prop():
    with given:
        director = DirectorPlugin(Director)
        init_event = DirectorInitEvent(director)

    with when:
        res = init_event.director

    with then:
        assert res == director


def test_director_init_event_repr():
    with given:
        director = DirectorPlugin(Director)
        init_event = DirectorInitEvent(director)

    with when:
        res = repr(init_event)

    with then:
        assert res == f"DirectorInitEvent({director!r})"
