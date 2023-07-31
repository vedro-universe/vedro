from abc import ABC, abstractmethod
from typing import Set

__all__ = ("And", "Or", "Not", "Operand", "Operator", "Expr",)


class Expr(ABC):
    @abstractmethod
    def __call__(self, tags: Set[str]) -> bool:
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass


class Operator(Expr, ABC):
    pass


class Operand(Expr):
    def __init__(self, tag: str) -> None:
        self._tag = tag

    def __call__(self, tags: Set[str]) -> bool:
        return self._tag in tags

    def __repr__(self) -> str:
        return f"Tag({self._tag})"


class And(Operator):
    def __init__(self, left: Operand, right: Operand) -> None:
        self._left = left
        self._right = right

    def __call__(self, tags: Set[str]) -> bool:
        return self._left(tags) and self._right(tags)

    def __repr__(self) -> str:
        return f"And({self._left}, {self._right})"


class Or(Operator):
    def __init__(self, left: Operand, right: Operand) -> None:
        self._left = left
        self._right = right

    def __call__(self, tags: Set[str]) -> bool:
        return self._left(tags) or self._right(tags)

    def __repr__(self) -> str:
        return f"Or({self._left}, {self._right})"


class Not(Operator):
    def __init__(self, operand: Operand) -> None:
        self._operand = operand

    def __call__(self, tags: Set[str]) -> bool:
        return not self._operand(tags)

    def __repr__(self) -> str:
        return f"Not({self._operand})"
