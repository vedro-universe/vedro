import ast
from ast import dump

from baby_steps import given, then, when
from pytest import warns

from vedro.plugins.assert_rewriter import NodeAssertRewriter


def test_rewrite_assert():
    with given:
        rewriter = NodeAssertRewriter("assert_tool", {ast.Eq: "assert_equal"})
        tree = ast.parse("assert x == y")

    with when:
        rewritten_tree = rewriter.visit(tree)

    with then:
        assert dump(rewritten_tree) == dump(ast.parse(
            "assert assert_tool.assert_equal(x, y)"
        ))


def test_rewrite_assert_with_message():
    with given:
        rewriter = NodeAssertRewriter("assert_tool", {ast.Eq: "assert_equal"})
        tree = ast.parse("assert x == y, 'x should be equal to y'")

    with when:
        rewritten_tree = rewriter.visit(tree)

    with then:
        assert dump(rewritten_tree) == dump(ast.parse(
            "assert assert_tool.assert_equal(x, y, message='x should be equal to y')"
        ))


def test_rewrite_assert_multiple_comparisons():
    with given:
        rewriter = NodeAssertRewriter("assert_tool", {
            ast.Lt: "assert_less",
            ast.LtE: "assert_less_equal",
        })
        tree = ast.parse("assert x < y <= z")

    with when:
        rewritten_tree = rewriter.visit(tree)

    with then:
        assert dump(rewritten_tree) == dump(ast.parse(
            "assert assert_tool.assert_less(x, y) and assert_tool.assert_less_equal(y, z)"
        ))


def test_rewrite_assert_truthy():
    with given:
        rewriter = NodeAssertRewriter("assert_tool", {type(None): "assert_truthy"})
        tree = ast.parse("assert x")

    with when:
        rewritten_tree = rewriter.visit(tree)

    with then:
        assert dump(rewritten_tree) == dump(ast.parse(
            "assert assert_tool.assert_truthy(x)"
        ))


def test_rewrite_assert_unsupported_operator():
    with given:
        rewriter = NodeAssertRewriter("assert_tool", {})
        tree = ast.parse("assert x is y")

    with when, warns(Warning) as record:
        rewritten_tree = rewriter.visit(tree)

    with then:
        assert dump(rewritten_tree) == dump(tree)

        warning_message = str(record.list[0].message)
        assert "NodeAssertRewriter: Unsupported operator" in warning_message
        assert "<ast.Is object" in warning_message
