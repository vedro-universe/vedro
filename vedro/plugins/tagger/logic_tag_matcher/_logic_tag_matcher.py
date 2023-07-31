from re import fullmatch
from typing import Set, cast

from pyparsing import Literal
from pyparsing import ParserElement as Parser
from pyparsing import ParseResults, Regex, infixNotation, opAssoc
from pyparsing.exceptions import ParseException

from .._tag_matcher import TagMatcher
from ._logic_ops import And, Expr, Not, Operand, Or

__all__ = ("LogicTagMatcher",)


class LogicTagMatcher(TagMatcher):
    tag_pattern = r'(?!and$|or$|not$)[A-Za-z_][A-Za-z0-9_]*'

    def __init__(self, expr: str) -> None:
        super().__init__(expr)
        operand = Regex(self.tag_pattern).setParseAction(self._create_tag)
        self._parser = infixNotation(operand, [
            (Literal("not"), 1, opAssoc.RIGHT, self._create_not),
            (Literal("and"), 2, opAssoc.LEFT, self._create_and),
            (Literal("or"), 2, opAssoc.LEFT, self._create_or),
        ])
        self._grammar = self._parse(self._parser, expr)

    def match(self, tags: Set[str]) -> bool:
        return self._grammar(tags)

    def validate(self, tag: str) -> bool:
        return fullmatch(self.tag_pattern, tag) is not None

    def _create_tag(self, orig: str, location: int, tokens: ParseResults) -> Expr:
        tag = tokens[0]
        return Operand(tag)

    def _create_not(self, orig: str, location: int, tokens: ParseResults) -> Expr:
        operand = tokens[0][-1]
        return Not(operand)

    def _create_and(self, orig: str, location: int, tokens: ParseResults) -> Expr:
        left = tokens[0][0]
        right = tokens[0][-1]
        return And(left, right)

    def _create_or(self, orig: str, location: int, tokens: ParseResults) -> Expr:
        left = tokens[0][0]
        right = tokens[0][-1]
        return Or(left, right)

    def _parse(self, grammar: Parser, expr: str) -> Expr:
        try:
            results = grammar.parse_string(expr, parse_all=True)
        except ParseException as e:
            raise ValueError(f"Invalid tag expr {expr!r}. Error: {str(e)}") from None

        if len(results) == 0:
            raise ValueError(f"Invalid tag expr {expr!r}")
        return cast(Expr, results[0])
