import re
from re import fullmatch
from typing import Set, Union, cast

from pyparsing import CaselessKeyword
from pyparsing import ParserElement as Parser
from pyparsing import ParseResults, Regex, infixNotation, opAssoc
from pyparsing.exceptions import ParseException

from .._tag_matcher import TagMatcher
from ._logic_ops import And, Expr, Not, Operand, Or

__all__ = ("LogicTagMatcher",)


class LogicTagMatcher(TagMatcher):
    """
    Implements a tag matcher that evaluates logical expressions using the `And`, `Or`,
    and `Not` operators.

    This class parses a logical expression string consisting of operands (tags) and logical
    operators, and evaluates whether a given set of tags satisfies the parsed expression.
    Tags are checked for membership in the set, and logical operators are applied according to
    standard boolean logic.
    """

    tag_pattern = r'(?!and$|or$|not$)[A-Za-z_][A-Za-z0-9_]*'

    def __init__(self, expr: str) -> None:
        """
        Initialize the LogicTagMatcher with a logical expression string.

        :param expr: The logical expression string to parse and evaluate.
                     The expression can contain tag names, 'and', 'or', 'not' logical operators.
        """
        super().__init__(expr)
        operand = Regex(self.tag_pattern, re.IGNORECASE).setParseAction(self._create_tag)
        self._parser = infixNotation(operand, [
            (CaselessKeyword("not"), 1, opAssoc.RIGHT, self._create_not),
            (CaselessKeyword("and"), 2, opAssoc.LEFT, self._create_and),
            (CaselessKeyword("or"), 2, opAssoc.LEFT, self._create_or),
        ])
        self._grammar: Union[Expr, None] = None

    def match(self, tags: Set[str]) -> bool:
        """
        Match the provided set of tags against the parsed logical expression.

        :param tags: A set of strings representing tags to evaluate.
        :return: True if the set of tags satisfies the logical expression, False otherwise.
        """
        if self._grammar is None:
            self._grammar = self._parse(self._parser, self._expr)
        return self._grammar(tags)

    def validate(self, tag: str) -> bool:
        """
        Validate whether a tag conforms to the allowed tag pattern.

        :param tag: The tag to validate.
        :return: True if the tag is valid, raises an exception otherwise.
        :raises TypeError: If the tag is not a string.
        :raises ValueError: If the tag does not match the required pattern, or if it is a
                            reserved keyword.
        """
        if not isinstance(tag, str):
            raise TypeError(f"Tag must be a str, got {type(tag)}")

        res = fullmatch(self.tag_pattern, tag, re.IGNORECASE)
        if res is None:
            raise ValueError("Tags must start with a letter or underscore, "
                             "followed by letters, digits, or underscores. "
                             "Reserved keywords 'and', 'or', and 'not' are not allowed.")

        return True

    def _create_tag(self, orig: str, location: int, tokens: ParseResults) -> Expr:
        """
        Create an Operand expression from a parsed tag.

        :param orig: The original input string (unused).
        :param location: The location of the match in the string (unused).
        :param tokens: The parsed tokens, where the first token is the tag.
        :return: An Operand instance representing the parsed tag.
        """
        tag = tokens[0]
        return Operand(tag)

    def _create_not(self, orig: str, location: int, tokens: ParseResults) -> Expr:
        """
        Create a Not operator expression from parsed tokens.

        :param orig: The original input string (unused).
        :param location: The location of the match in the string (unused).
        :param tokens: The parsed tokens, where the operand to negate is in the tokens.
        :return: A Not instance representing the negation of the operand.
        """
        operand = tokens[0][-1]
        return Not(operand)

    def _create_and(self, orig: str, location: int, tokens: ParseResults) -> Expr:
        """
        Create an And operator expression from parsed tokens.

        :param orig: The original input string (unused).
        :param location: The location of the match in the string (unused).
        :param tokens: The parsed tokens, where the first token is the left operand and
                       the last token is the right operand.
        :return: An And instance representing the logical AND of the two operands.
        """
        exprs = tokens[0][::2]
        result = exprs[0]
        for e in exprs[1:]:
            result = And(result, e)
        return cast(Expr, result)

    def _create_or(self, orig: str, location: int, tokens: ParseResults) -> Expr:
        """
        Create an Or operator expression from parsed tokens.

        :param orig: The original input string (unused).
        :param location: The location of the match in the string (unused).
        :param tokens: The parsed tokens, where the first token is the left operand and
                       the last token is the right operand.
        :return: An Or instance representing the logical OR of the two operands.
        """
        exprs = tokens[0][::2]
        result = exprs[0]
        for e in exprs[1:]:
            result = Or(result, e)
        return cast(Expr, result)

    def _parse(self, grammar: Parser, expr: str) -> Expr:
        """
        Parse the provided logical expression using the grammar.

        :param grammar: The parser grammar to use for parsing the expression.
        :param expr: The logical expression string to parse.
        :return: An Expr instance representing the parsed logical expression.
        :raises ValueError: If the expression is invalid or cannot be parsed.
        """
        try:
            results = grammar.parse_string(expr, parse_all=True)
        except ParseException as e:
            raise ValueError(f"Invalid tag expr {expr!r}. Error: {str(e)}") from None

        if len(results) == 0:
            raise ValueError(f"Invalid tag expr {expr!r}")
        return cast(Expr, results[0])
