from enum import Enum
from typing import Any, Union

from niltype import Nil, Nilable, NilType

__all__ = ("assert_", "AssertionTool", "CompareOperator",)


class CompareOperator(str, Enum):
    """
    Defines comparison operators for assertions.

    This enumeration provides string representations for comparison operators used in assertions.
    """

    EQUAL = "=="
    NOT_EQUAL = "!="
    LESS = "<"
    LESS_EQUAL = "<="
    GREATER = ">"
    GREATER_EQUAL = ">="
    IS = "is"
    IS_NOT = "is not"
    IN = "in"
    NOT_IN = "not in"

    def __str__(self) -> str:
        """
        Return the string representation of the comparison operator.

        :return: The string representation of the comparison operator.
        """
        return self.value


class AssertionTool:
    """
    Provides custom assertion methods.

    This class includes methods to perform various assertions, raising detailed
    assertion errors when conditions are not met.
    """

    def assert_truthy(self, left: Any, message: Nilable[Any] = Nil) -> bool:
        """
        Assert that the value is truthy.

        :param left: The value to check for truthiness.
        :param message: An optional message to include in the assertion error.
        :return: True if the value is truthy.
        :raises AssertionError: If the value is not truthy.
        """
        if left:
            return True
        raise self._create_assertion_error(left=left, message=message)

    def assert_equal(self, left: Any, right: Any, message: Nilable[Any] = Nil) -> bool:
        """
        Assert that two values are equal.

        :param left: The first value to compare.
        :param right: The second value to compare.
        :param message: An optional message to include in the assertion error.
        :return: True if the values are equal.
        :raises AssertionError: If the values are not equal.
        """
        if left == right:
            return True
        raise self._create_assertion_error(left=left, right=right,
                                           operator=CompareOperator.EQUAL,
                                           message=message)

    def assert_not_equal(self, left: Any, right: Any, message: Nilable[Any] = Nil) -> bool:
        """
        Assert that two values are not equal.

        :param left: The first value to compare.
        :param right: The second value to compare.
        :param message: An optional message to include in the assertion error.
        :return: True if the values are not equal.
        :raises AssertionError: If the values are equal.
        """
        if left != right:
            return True

        raise self._create_assertion_error(left=left, right=right,
                                           operator=CompareOperator.NOT_EQUAL,
                                           message=message)

    def assert_less(self, left: Any, right: Any, message: Nilable[Any] = Nil) -> bool:
        """
        Assert that the first value is less than the second value.

        :param left: The first value to compare.
        :param right: The second value to compare.
        :param message: An optional message to include in the assertion error.
        :return: True if the first value is less than the second value.
        :raises AssertionError: If the first value is not less than the second value.
        """
        if left < right:
            return True
        raise self._create_assertion_error(left=left, right=right,
                                           operator=CompareOperator.LESS,
                                           message=message)

    def assert_less_equal(self, left: Any, right: Any, message: Nilable[Any] = Nil) -> bool:
        """
        Assert that the first value is less than or equal to the second value.

        :param left: The first value to compare.
        :param right: The second value to compare.
        :param message: An optional message to include in the assertion error.
        :return: True if the first value is less than or equal to the second value.
        :raises AssertionError: If the first value is not less than or equal to the second value.
        """
        if left <= right:
            return True
        raise self._create_assertion_error(left=left, right=right,
                                           operator=CompareOperator.LESS_EQUAL,
                                           message=message)

    def assert_greater(self, left: Any, right: Any, message: Nilable[Any] = Nil) -> bool:
        """
        Assert that the first value is greater than the second value.

        :param left: The first value to compare.
        :param right: The second value to compare.
        :param message: An optional message to include in the assertion error.
        :return: True if the first value is greater than the second value.
        :raises AssertionError: If the first value is not greater than the second value.
        """
        if left > right:
            return True
        raise self._create_assertion_error(left=left, right=right,
                                           operator=CompareOperator.GREATER,
                                           message=message)

    def assert_greater_equal(self, left: Any, right: Any, message: Nilable[Any] = Nil) -> bool:
        """
        Assert that the first value is greater than or equal to the second value.

        :param left: The first value to compare.
        :param right: The second value to compare.
        :param message: An optional message to include in the assertion error.
        :return: True if the first value is greater than or equal to the second value.
        :raises AssertionError: If the first value is not greater than or equal
            to the second value.
        """
        if left >= right:
            return True

        raise self._create_assertion_error(left=left, right=right,
                                           operator=CompareOperator.GREATER_EQUAL,
                                           message=message)

    def assert_is(self, left: Any, right: Any, message: Nilable[Any] = Nil) -> bool:
        """
        Assert that the first value is the same object as the second value.

        :param left: The first value to compare.
        :param right: The second value to compare.
        :param message: An optional message to include in the assertion error.
        :return: True if the first value is the same object as the second value.
        :raises AssertionError: If the first value is not the same object as the second value.
        """
        if left is right:
            return True
        raise self._create_assertion_error(left=left, right=right,
                                           operator=CompareOperator.IS,
                                           message=message)

    def assert_is_not(self, left: Any, right: Any, message: Nilable[Any] = Nil) -> bool:
        """
        Assert that the first value is not the same object as the second value.

        :param left: The first value to compare.
        :param right: The second value to compare.
        :param message: An optional message to include in the assertion error.
        :return: True if the first value is not the same object as the second value.
        :raises AssertionError: If the first value is the same object as the second value.
        """
        if left is not right:
            return True
        raise self._create_assertion_error(left=left, right=right,
                                           operator=CompareOperator.IS_NOT,
                                           message=message)

    def assert_in(self, left: Any, right: Any, message: Nilable[Any] = Nil) -> bool:
        """
        Assert that the first value is in the second value.

        :param left: The value to check for membership.
        :param right: The collection to check for membership.
        :param message: An optional message to include in the assertion error.
        :return: True if the first value is in the second value.
        :raises AssertionError: If the first value is not in the second value.
        """
        if left in right:
            return True
        raise self._create_assertion_error(left=left, right=right,
                                           operator=CompareOperator.IN,
                                           message=message)

    def assert_not_in(self, left: Any, right: Any, message: Nilable[Any] = Nil) -> bool:
        """
        Assert that the first value is not in the second value.

        :param left: The value to check for non-membership.
        :param right: The collection to check for non-membership.
        :param message: An optional message to include in the assertion error.
        :return: True if the first value is not in the second value.
        :raises AssertionError: If the first value is in the second value.
        """
        if left not in right:
            return True
        raise self._create_assertion_error(left=left, right=right,
                                           operator=CompareOperator.NOT_IN,
                                           message=message)

    def get_left(self, error: AssertionError) -> Union[Any, NilType]:
        """
        Get the left value from an assertion error.

        :param error: The assertion error.
        :return: The left value from the assertion error, or Nil if not set.
        """
        return getattr(error, "__vedro_assert_left__", Nil)

    def get_right(self, error: AssertionError) -> Union[Any, NilType]:
        """
        Get the right value from an assertion error.

        :param error: The assertion error.
        :return: The right value from the assertion error, or Nil if not set.
        """
        return getattr(error, "__vedro_assert_right__", Nil)

    def get_operator(self, error: AssertionError) -> Union[CompareOperator, NilType]:
        """
        Get the comparison operator from an assertion error.

        :param error: The assertion error.
        :return: The comparison operator from the assertion error, or Nil if not set.
        """
        return getattr(error, "__vedro_assert_operator__", Nil)

    def get_message(self, error: AssertionError) -> Union[Any, NilType]:
        """
        Get the message from an assertion error.

        :param error: The assertion error.
        :return: The message from the assertion error, or Nil if not set.
        """
        return getattr(error, "__vedro_assert_message__", Nil)

    def _create_assertion_error(self, *, left: Any,
                                right: Nilable[Any] = Nil,
                                operator: Nilable[CompareOperator] = Nil,
                                message: Nilable[Any] = Nil) -> AssertionError:
        """
        Create an AssertionError with detailed information.

        :param left: The left value of the assertion.
        :param right: The right value of the assertion, if any.
        :param operator: The comparison operator used in the assertion, if any.
        :param message: The message to include in the assertion error, if any.
        :return: An AssertionError with detailed information.
        """
        error = AssertionError(message if (message is not Nil) else "")

        setattr(error, "__vedro_assert_left__", left)

        if right is not Nil:
            setattr(error, "__vedro_assert_right__", right)

        if operator is not Nil:
            setattr(error, "__vedro_assert_operator__", operator)

        if message is not Nil:
            setattr(error, "__vedro_assert_message__", message)

        return error


assert_ = AssertionTool()
