from importlib.abc import Loader
from types import ModuleType
from typing import Any, final

from vedro.core import ModuleFileLoader

__all__ = ("LegacyAssertRewriterLoader",)


@final
class LegacyAssertRewriterLoader(ModuleFileLoader):
    """
    Handles legacy assertion rewriting.

    This class extends the ModuleFileLoader to support legacy assertion rewriting
    using the 'dessert' package. It ensures that modules are rewritten appropriately
    before execution.
    """

    def __init__(self, *, validate_module_names: bool = False, **kwargs: Any) -> None:
        """
        Initialize the LegacyAssertRewriter with optional validation for module names.

        :param validate_module_names: Whether to validate module names. Default is False.
        :param kwargs: Additional keyword arguments for the base class initializer.

        :raises ModuleNotFoundError: If the 'dessert' package is not installed.
        """
        super().__init__(validate_module_names=validate_module_names, **kwargs)

        try:
            from dessert import AssertionRewritingHook  # type: ignore
        except ModuleNotFoundError:  # pragma: no cover
            raise ModuleNotFoundError(
                "Package 'dessert' is not found, install it via 'pip install dessert'")
        else:
            self._rewriter = AssertionRewritingHook()

    def _exec_module(self, loader: Loader, module: ModuleType) -> None:
        """
        Execute the given module using the assertion rewriter.

        :param loader: The loader used to load the module.
        :param module: The module to be executed.
        """
        self._rewriter.exec_module(module)
