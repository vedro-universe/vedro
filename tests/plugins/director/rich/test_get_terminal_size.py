import os
from unittest.mock import patch

from baby_steps import given, then, when

from vedro.plugins.director.rich.utils import get_terminal_size


def test_get_terminal_size():
    with given:
        width, height = 1, 2
        terminal_size = os.terminal_size((width, height))

    with when, patch("shutil.get_terminal_size", return_value=terminal_size):
        res = get_terminal_size()

    with then:
        assert res == terminal_size


def test_get_terminal_size_default_fallback():
    with given:
        width, height = 80, 24
        terminal_size = os.terminal_size((0, 0))

    with when, patch("shutil.get_terminal_size", return_value=terminal_size):
        res = get_terminal_size(width, height)

    with then:
        assert res == os.terminal_size((80, 24))


def test_get_terminal_size_custom_fallback():
    with given:
        width, height = 1, 2
        terminal_size = os.terminal_size((0, 0))

    with when, patch("shutil.get_terminal_size", return_value=terminal_size):
        res = get_terminal_size(width, height)

    with then:
        assert res == os.terminal_size((width, height))
