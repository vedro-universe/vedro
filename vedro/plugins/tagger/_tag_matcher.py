from abc import ABC, abstractmethod
from typing import Set

__all__ = ("TagMatcher",)


class TagMatcher(ABC):
    """
    Defines an abstract base class for matching tags against a logical expression.

    Subclasses must implement the `match` method to evaluate if a set of tags satisfies
    a given expression, and the `validate` method to check if individual tags are valid.
    """

    def __init__(self, expr: str) -> None:
        """
        Initialize the TagMatcher with a logical expression string.

        :param expr: The logical expression string to be used for tag matching.
        """
        self._expr = expr

    @abstractmethod
    def match(self, tags: Set[str]) -> bool:
        """
        Evaluate whether the given set of tags matches the logical expression.

        :param tags: A set of strings representing the tags to evaluate.
        :return: True if the tags match the expression, False otherwise.
        """
        pass

    @abstractmethod
    def validate(self, tag: str) -> bool:
        """
        Validate whether a given tag conforms to expected rules or syntax.

        :param tag: The tag to validate.
        :return: True if the tag is valid, raises an exception otherwise.
        :raises TypeError: If the tag is not a string.
        :raises ValueError: If the tag does not conform to the expected format.
        """
        pass
