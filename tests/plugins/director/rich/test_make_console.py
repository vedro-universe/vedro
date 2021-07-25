from baby_steps import given, then, when
from rich.console import Console

from vedro.plugins.director.rich.utils import make_console


def test_make_console():
    with when:
        res = make_console()

    with then:
        assert isinstance(res, Console)


def test_make_console_custom_options():
    with given:
        width, height = 1, 2

    with when:
        res = make_console(width=width, height=height)

    with then:
        assert isinstance(res, Console)
        assert res.size == (width, height)
