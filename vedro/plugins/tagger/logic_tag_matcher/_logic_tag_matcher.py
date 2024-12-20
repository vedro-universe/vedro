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

    This class takes a logical expression string consisting of tag operands and logical
    operators, parses it into an expression tree, and then evaluates whether a given set of tags
    satisfies the parsed expression. Tags are checked for membership in the input set, and
    logical operators (and, or, not) are applied according to standard Boolean logic.
    """

    tag_pattern = r'(?!and$|or$|not$)[A-Za-z_][A-Za-z0-9_]*'

    def __init__(self, expr: str) -> None:
        """
        Initialize the LogicTagMatcher with a logical expression string.

        :param expr: The logical expression to parse, which may include tags and the
                     logical operators 'and', 'or', and 'not'. For example:
                     "(API and not CLI) or UI".
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
        Evaluate the parsed expression against a set of tags.

        :param tags: A set of strings representing tags to be tested against the expression.
        :return: True if the expression evaluates to True given the tags, False otherwise.
        """
        if self._grammar is None:
            self._grammar = self._parse(self._parser, self._expr)
        return self._grammar(tags)

    def validate(self, tag: str) -> bool:
        """
        Validate that a given tag name meets the required criteria:
        - Must be a string
        - Must match the pattern: start with a letter or underscore, followed by letters, digits,
          or underscores.
        - Must not be a reserved keyword ('and', 'or', 'not').

        :param tag: The tag to validate.
        :return: True if the tag is valid.
        :raises TypeError: If the tag is not a string.
        :raises ValueError: If the tag is invalid or a reserved keyword.
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

        This method is called when the parser recognizes a valid tag. It returns an Operand
        that checks for membership of the tag in a given set.

        :param orig: The original input string (unused).
        :param location: The location of the match in the string (unused).
        :param tokens: The parsed tokens, where the first token is the tag name.
        :return: An Operand instance for the parsed tag.
        """
        tag = tokens[0]
        return Operand(tag)

    def _create_not(self, orig: str, location: int, tokens: ParseResults) -> Expr:
        """
        Create a Not operator expression from parsed tokens.

        The 'not' operator is unary, so this method is called when the parser recognizes a
        pattern like "not <operand>". It returns a Not instance that negates the operand's result.

        :param orig: The original input string (unused).
        :param location: The location of the match in the string (unused).
        :param tokens: The parsed tokens, which will contain a single operand to be negated.
        :return: A Not instance representing the negation of the operand.
        """
        operand = tokens[0][-1]
        return Not(operand)

    def _create_and(self, orig: str, location: int, tokens: ParseResults) -> Expr:
        """
        Create an And operator expression from parsed tokens.

        For chained 'and' operations, the parser may return multiple operands. For example,
        parsing "A and B and C" may produce tokens like [[A, 'and', B, 'and', C]].
        This method extracts all operands and folds them from left to right into nested And
        expressions:
        "A and B and C" -> And(And(A, B), C)

        :param orig: The original input string (unused).
        :param location: The location of the match in the string (unused).
        :param tokens: The parsed tokens, which may include multiple operands and 'and' operators.
        :return: A nested And expression representing the logical AND of all operands.
        """
        exprs = tokens[0][::2]
        result = exprs[0]
        for e in exprs[1:]:
            result = And(result, e)
        return cast(Expr, result)

    def _create_or(self, orig: str, location: int, tokens: ParseResults) -> Expr:
        """
        Create an Or operator expression from parsed tokens.

        Similar to the 'and' operator handling, multiple operands can be chained with 'or'.
        For example, "A or B or C" may yield tokens [[A, 'or', B, 'or', C]].
        This method extracts all operands and folds them into nested Or expressions:
        "A or B or C" -> Or(Or(A, B), C)

        :param orig: The original input string (unused).
        :param location: The location of the match in the string (unused).
        :param tokens: The parsed tokens, which may include multiple operands and 'or' operators.
        :return: A nested Or expression representing the logical OR of all operands.
        """
        exprs = tokens[0][::2]
        result = exprs[0]
        for e in exprs[1:]:
            result = Or(result, e)
        return cast(Expr, result)

    def _parse(self, grammar: Parser, expr: str) -> Expr:
        """
        Parse the provided logical expression using the defined grammar.

        :param grammar: The parser grammar to use for parsing the expression.
        :param expr: The logical expression string to parse.
        :return: An Expr instance representing the parsed logical expression tree.
        :raises ValueError: If the expression is invalid or cannot be parsed.
        """
        try:
            results = grammar.parse_string(expr, parse_all=True)
        except ParseException as e:
            raise ValueError(f"Invalid tag expr {expr!r}. Error: {str(e)}") from None

        if len(results) == 0:
            raise ValueError(f"Invalid tag expr {expr!r}")
        return cast(Expr, results[0])
