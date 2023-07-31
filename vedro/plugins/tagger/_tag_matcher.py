from abc import ABC, abstractmethod
from typing import Set

__all__ = ("TagMatcher",)


class TagMatcher(ABC):
    def __init__(self, expr: str) -> None:
        self._expr = expr

    @abstractmethod
    def match(self, tags: Set[str]) -> bool:
        pass

    @abstractmethod
    def validate(self, tag: str) -> bool:
        pass
