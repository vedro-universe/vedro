from abc import ABC, abstractmethod
from typing import Set

__all__ = ("And", "Or", "Not", "Operand", "Operator", "Expr",)


class Expr(ABC):
    """
    Represents an abstract base class for all expressions.

    This class provides an interface for evaluating logical expressions
    on a set of tags. It must be subclassed by specific expression types
    like operands and operators.
    """

    @abstractmethod
    def __call__(self, tags: Set[str]) -> bool:
        """
        Evaluate the expression based on the provided tags.

        :param tags: A set of strings representing tags to evaluate.
        :return: A boolean result of the evaluation.
        """
        pass

    @abstractmethod
    def __repr__(self) -> str:
        """
        Return a string representation of the expression.

        :return: A string representation of the expression.
        """
        pass


class Operator(Expr, ABC):
    """
    Serves as an abstract base class for logical operators.

    Logical operators (e.g., And, Or, Not) combine or modify operands and are
    used to construct complex logical expressions.
    """
    pass


class Operand(Expr):
    """
    Represents an operand in a logical expression.

    An operand is a tag that is checked for membership in a given set of tags.
    """

    def __init__(self, tag: str) -> None:
        """
        Initialize the Operand with a specific tag.

        :param tag: The tag to be checked in a set of tags.
        """
        self._tag = tag

    def __call__(self, tags: Set[str]) -> bool:
        """
        Check if the operand's tag is present in the provided set of tags.

        :param tags: A set of strings representing tags to evaluate.
        :return: True if the tag is in the set, False otherwise.
        """
        return self._tag in tags

    def __repr__(self) -> str:
        """
        Return a string representation of the operand.

        :return: A string in the form 'Tag(tag)'.
        """
        return f"Tag({self._tag})"


class And(Operator):
    """
    Represents a logical AND operation between two operands.

    The result of the AND operation is True if both operands evaluate to True
    when applied to a set of tags.
    """

    def __init__(self, left: Operand, right: Operand) -> None:
        """
        Initialize the And operator with two operands.

        :param left: The left operand in the AND operation.
        :param right: The right operand in the AND operation.
        """
        self._left = left
        self._right = right

    def __call__(self, tags: Set[str]) -> bool:
        """
        Evaluate the AND operation on the provided set of tags.

        :param tags: A set of strings representing tags to evaluate.
        :return: True if both the left and right operands evaluate to True, False otherwise.
        """
        return self._left(tags) and self._right(tags)

    def __repr__(self) -> str:
        """
        Return a string representation of the AND operation.

        :return: A string in the form 'And(left_operand, right_operand)'.
        """
        return f"And({self._left}, {self._right})"


class Or(Operator):
    """
    Represents a logical OR operation between two operands.

    The result of the OR operation is True if either operand evaluates to True
    when applied to a set of tags.
    """

    def __init__(self, left: Operand, right: Operand) -> None:
        """
        Initialize the Or operator with two operands.

        :param left: The left operand in the OR operation.
        :param right: The right operand in the OR operation.
        """
        self._left = left
        self._right = right

    def __call__(self, tags: Set[str]) -> bool:
        """
        Evaluate the OR operation on the provided set of tags.

        :param tags: A set of strings representing tags to evaluate.
        :return: True if either the left or right operand evaluates to True, False otherwise.
        """
        return self._left(tags) or self._right(tags)

    def __repr__(self) -> str:
        """
        Return a string representation of the OR operation.

        :return: A string in the form 'Or(left_operand, right_operand)'.
        """
        return f"Or({self._left}, {self._right})"


class Not(Operator):
    """
    Represents a logical NOT operation on a single operand.

    The result of the NOT operation is True if the operand evaluates to False
    when applied to a set of tags, and False if the operand evaluates to True.
    """

    def __init__(self, operand: Operand) -> None:
        """
        Initialize the Not operator with a single operand.

        :param operand: The operand to be negated in the NOT operation.
        """
        self._operand = operand

    def __call__(self, tags: Set[str]) -> bool:
        """
        Evaluate the NOT operation on the provided set of tags.

        :param tags: A set of strings representing tags to evaluate.
        :return: True if the operand evaluates to False, False if the operand evaluates to True.
        """
        return not self._operand(tags)

    def __repr__(self) -> str:
        """
        Return a string representation of the NOT operation.

        :return: A string in the form 'Not(operand)'.
        """
        return f"Not({self._operand})"
