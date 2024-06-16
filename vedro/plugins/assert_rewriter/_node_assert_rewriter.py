import ast
import warnings
from typing import Any, Dict, List, Optional, Union

from niltype import Nil

__all__ = ("NodeAssertRewriter",)


class NodeAssertRewriter(ast.NodeTransformer):
    """
    Transforms assert statements into calls to custom assertion methods.

    This class rewrites assert statements in the abstract syntax tree (AST)
    to use a specified assertion tool with custom assertion methods.
    """

    def __init__(self, assert_tool: str, assert_methods: Dict[Any, str]) -> None:
        """
        Initialize the AssertRewriter with the specified assertion tool and methods.

        :param assert_tool: The tool used for assertions.
        :param assert_methods: A dictionary mapping AST comparison operators to assertion methods.
        """
        super().__init__()
        self._assert_tool = assert_tool
        self._assert_methods = assert_methods

    def visit_Assert(self, node: ast.Assert) -> ast.Assert:
        """
        Visit assert nodes and rewrite them using the custom assertion methods.

        :param node: The assert node in the AST.
        :return: The rewritten assert node or the original if rewriting fails.
        """
        try:
            new_node = self._rewrite_expr(node.test, node.msg)
        except:  # noqa
            return node
        else:
            ast.copy_location(new_node, node)
            ast.fix_missing_locations(new_node)
            return new_node

    def _rewrite_expr(self, node: ast.expr, msg: Union[ast.AST, None] = None) -> ast.Assert:
        """
        Rewrite the expression of an assert node.

        :param node: The expression node in the assert statement.
        :param msg: The message node in the assert statement, if any.
        :return: A new assert node with the rewritten expression.
        """
        if isinstance(node, ast.Compare):
            return self._rewrite_compare(node, msg)
        return ast.Assert(test=self._create_assert(node, msg=msg), msg=None)

    def _rewrite_compare(self, node: ast.Compare, msg: Optional[ast.AST] = None) -> ast.Assert:
        """
        Rewrite a comparison expression in an assert statement.

        :param node: The comparison node in the assert statement.
        :param msg: The message node in the assert statement, if any.
        :return: A new assert node with the rewritten comparison expression.
        """
        assertions = []

        left = node.left
        for op, right in zip(node.ops, node.comparators):
            assert_expr = self._create_assert(left, right, op, msg)
            assertions.append(assert_expr)
            left = right

        and_expr = assertions[0]
        for assert_expr in assertions[1:]:
            and_expr = ast.BoolOp(op=ast.And(), values=[and_expr, assert_expr])  # type: ignore

        return ast.Assert(test=and_expr, msg=None)

    def _create_assert(self, left: ast.AST,
                       right: Optional[ast.AST] = None,
                       operator: Optional[ast.AST] = None,
                       msg: Optional[ast.AST] = None) -> ast.Call:
        """
        Create an assertion call.

        :param left: The left operand of the assertion.
        :param right: The right operand of the assertion, if any.
        :param operator: The comparison operator, if any.
        :param msg: The message for the assertion, if any.
        :return: An AST node representing the assertion call.
        :raises ValueError: If the operator is unsupported.
        """
        args = [left, right] if (right is not None) else [left]
        keywords = [ast.keyword(arg="message", value=msg)] if (msg is not None) else []

        method = self._assert_methods.get(type(operator), Nil)
        if method is not Nil:
            return self._create_assert_call(method, args, keywords)
        else:
            warnings.warn(f"NodeAssertRewriter: Unsupported operator '{operator}'")
            raise ValueError(f"Unsupported operator: '{operator}'")

    def _create_assert_call(self, method: str,
                            args: List[ast.AST],
                            kwargs: List[ast.keyword]) -> ast.Call:
        """
        Create an AST node for an assertion call.

        :param method: The method name of the assertion.
        :param args: The arguments for the assertion.
        :param kwargs: The keyword arguments for the assertion.
        :return: An AST call node for the assertion.
        """
        return ast.Call(
            func=ast.Attribute(
                value=ast.Name(id=self._assert_tool, ctx=ast.Load()),
                attr=method,
                ctx=ast.Load()
            ),
            args=args,
            keywords=kwargs
        )
