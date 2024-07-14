import ast
import inspect
from importlib.abc import Loader
from types import ModuleType
from typing import Any, cast, final

from vedro.core import ModuleFileLoader

from ._node_assert_rewriter import NodeAssertRewriter
from ._typing import override

__all__ = ("AssertRewriterLoader",)


@final
class AssertRewriterLoader(ModuleFileLoader):
    """
    Loads and rewrites Python modules to use custom assertion methods.

    This class extends ModuleFileLoader to rewrite assert statements in Python
    modules to use a specified assertion tool with custom assertion methods.
    """

    assert_module = "vedro.plugins.assert_rewriter"
    assert_tool = "assert_"
    assert_methods = {
        ast.Eq: "assert_equal",
        ast.NotEq: "assert_not_equal",

        ast.Lt: "assert_less",
        ast.LtE: "assert_less_equal",
        ast.Gt: "assert_greater",
        ast.GtE: "assert_greater_equal",

        ast.Is: "assert_is",
        ast.IsNot: "assert_is_not",

        ast.In: "assert_in",
        ast.NotIn: "assert_not_in",

        type(None): "assert_truthy",
    }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the AssertRewriterModuleLoader.

        :param args: Positional arguments for the base class.
        :param kwargs: Keyword arguments for the base class.
        """
        super().__init__(*args, **kwargs)
        self._assert_rewriter = NodeAssertRewriter(
            assert_tool=self.assert_tool,
            assert_methods=self.assert_methods
        )

    @override
    def _exec_module(self, loader: Loader, module: ModuleType) -> None:
        """
        Execute the module after rewriting its assert statements.

        :param loader: The loader used to load the module.
        :param module: The module to execute.
        """
        source_code = inspect.getsource(module)

        tree = ast.parse(source_code)
        rewritten_tree = self._rewrite_tree(tree)

        transformed = compile(rewritten_tree, module.__file__, "exec")  # type: ignore
        exec(transformed, module.__dict__)

    def _rewrite_tree(self, tree: ast.Module) -> ast.Module:
        """
        Rewrite the AST of the module to replace assert statements.

        :param tree: The AST of the module.
        :return: The rewritten AST of the module.
        """
        rewritten_tree = self._assert_rewriter.visit(tree)

        import_stmt = ast.ImportFrom(
            module=self.assert_module,
            names=[ast.alias(name=self.assert_tool, asname=None)],
            level=0
        )
        ast.fix_missing_locations(import_stmt)
        rewritten_tree.body.insert(0, import_stmt)

        return cast(ast.Module, rewritten_tree)
