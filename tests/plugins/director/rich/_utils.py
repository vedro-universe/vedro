from unittest.mock import Mock

import pytest
from rich.console import Console

from vedro.plugins.director.rich import RichPrinter


@pytest.fixture()
def console_() -> Mock:
    return Mock(Console)


@pytest.fixture()
def printer(console_: Mock) -> RichPrinter:
    return RichPrinter(lambda: console_)
