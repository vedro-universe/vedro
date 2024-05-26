import ast
import inspect
from importlib.abc import Loader
from types import ModuleType
from typing import Any, Optional

from vedro.core import ModuleFileLoader

__all__ = ("AssertRewriterModuleLoader",)


def assert_eq(left: Any, right: Any, message: Optional[str] = None) -> bool:
    if left != right:
        exc = AssertionError(message)
        exc.__vedro_assert_left__ = left  # type: ignore
        exc.__vedro_assert_right__ = right  # type: ignore
        exc.__vedro_assert_message__ = message  # type: ignore
        raise exc

    return True


class AssertRewriter(ast.NodeTransformer):
    def visit_Assert(self, node: ast.Assert) -> ast.Assert:
        if not isinstance(node.test, ast.Compare):
            return node

        if not len(node.test.ops) == 1:
            return node

        if not isinstance(node.test.ops[0], ast.Eq):
            return node

        msg = node.msg if node.msg else ast.Constant(value="", kind=None)
        new_node = ast.Assert(
            test=ast.Call(
                func=ast.Name(id='assert_eq', ctx=ast.Load()),
                args=[node.test.left, node.test.comparators[0], msg],
                keywords=[],
            ),
        )

        ast.copy_location(new_node, node)
        ast.fix_missing_locations(new_node)

        return new_node


class AssertRewriterModuleLoader(ModuleFileLoader):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._assert_rewriter = AssertRewriter()

        __builtins__["assert_eq"] = assert_eq

    def _exec_module(self, loader: Loader, module: ModuleType) -> None:
        source_code = inspect.getsource(module)

        tree = ast.parse(source_code)
        tree = self._assert_rewriter.visit(tree)

        transformed = compile(tree, module.__file__, "exec")  # type: ignore
        exec(transformed, module.__dict__)
