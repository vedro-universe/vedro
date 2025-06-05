from types import TracebackType
from typing import Optional, Type, Union

__all__ = ("given", "when", "then", "Given", "When", "Then", "Step",)


class Step:
    def __init__(self) -> None:
        self._name: Union[str, None] = None

    def __enter__(self) -> None:
        pass

    async def __aenter__(self) -> None:
        return self.__enter__()

    def __exit__(self,
                 exc_type: Optional[Type[BaseException]],
                 exc_val: Optional[BaseException],
                 exc_tb: Optional[TracebackType]) -> bool:
        self._name = None
        return exc_type is None

    async def __aexit__(self,
                        exc_type: Optional[Type[BaseException]],
                        exc_val: Optional[BaseException],
                        exc_tb: Optional[TracebackType]) -> bool:
        return self.__exit__(exc_type, exc_val, exc_tb)

    def __call__(self, name: str) -> "Step":
        self._name = name
        return self


class Given(Step):
    pass


class When(Step):
    pass


class Then(Step):
    pass


given = Given()
when = When()
then = Then()
