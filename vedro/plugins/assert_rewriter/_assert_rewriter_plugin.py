import sys
from pathlib import Path
from typing import List, Type, final

from vedro.core import ConfigType, Dispatcher, Plugin, PluginConfig
from vedro.events import ArgParsedEvent, ArgParseEvent, ConfigLoadedEvent

from ._assert_rewriter_finder import AssertRewriterFinder, RewritePathsType
from ._assert_rewriter_loader import AssertRewriterLoader
from ._legacy_assert_rewriter_loader import LegacyAssertRewriterLoader

__all__ = ("AssertRewriter", "AssertRewriterPlugin",)


# While assertion rewriting might initially seem like a tricky—or even hacky—
# approach, it is in fact a deliberate and pragmatic solution that delivers
# expressive failure reports without forcing the user into a custom assert API.
#
# 1. Bypassing Python’s Limitations
#    ------------------------------
#    At runtime, Python reduces `assert left OP right` to a Boolean check and,
#    on failure, raises a bare `AssertionError`. The original left/right
#    expressions and the operator are discarded. During module import, the
#    loader amends the abstract-syntax tree (AST) so that this missing
#    meta-information is preserved, implemented in the most straightforward
#    manner possible.
#
# 2. Developer Ergonomics / Experience
#    ---------------------------------
#    Without rewriting, a test author would need to remember helper functions
#    such as `assert_eq()` or `assert_isinstance()`, import them in every file,
#    and wrap each comparison manually—making tests less readable, harder to
#    write, and more tedious to maintain. Rewriting lets the author keep
#    idiomatic asserts, and when one fails, Vedro’s reporters can display a
#    coloured diff of the mismatched values — exactly what developers expect,
#    rather than Python’s cryptic traceback.
#
# 3. Zero Behavioral Impact
#    ----------------------
#    The transformation acts as a compile-time pre-processor that preserves the
#    exact semantics of the original code. It doesn’t alter control flow,
#    introduce side effects, or slow down execution in any measurable way. Its
#    sole purpose is to enrich the resulting `AssertionError` with additional
#    context, so reporters can render precise, readable diffs. In that sense, it
#    is conceptually identical to the miniature AST edits that debugging or
#    coverage tools perform, just laser-focused on assertions.


@final
class AssertRewriterPlugin(Plugin):
    """
    Manages the assertion rewriting mechanism for enhanced error messages.

    This plugin subscribes to various events to configure the assertion rewriter
    based on command-line arguments and configuration settings.
    """

    def __init__(self, config: Type["AssertRewriter"]):
        """
        Initialize the AssertRewriterPlugin with the specified configuration.

        :param config: The configuration class for the AssertRewriter plugin.
        """
        super().__init__(config)
        self._legacy_assertions = config.legacy_assertions
        self._assert_rewrite_paths = config.assert_rewrite_paths

    def subscribe(self, dispatcher: Dispatcher) -> None:
        """
        Subscribe to relevant events to handle configuration and argument parsing.

        :param dispatcher: The event dispatcher to subscribe to.
        """
        dispatcher.listen(ConfigLoadedEvent, self.on_config_loaded) \
                  .listen(ArgParseEvent, self.on_arg_parse) \
                  .listen(ArgParsedEvent, self.on_arg_parsed)

    def on_config_loaded(self, event: ConfigLoadedEvent) -> None:
        """
        Handle the event when the configuration is loaded.

        :param event: The configuration loaded event containing the global config.
        """
        self._global_config: ConfigType = event.config

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        """
        Handle the event to parse command-line arguments.

        Adds an argument to enable legacy assertion rewriting for backwards compatibility.

        :param event: The argument parse event containing the argument parser.
        """
        help_message = "Use legacy assertion rewriter for backwards compatibility"
        event.arg_parser.add_argument("--legacy-assertions", action="store_true",
                                      default=self._legacy_assertions, help=help_message)

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        """
        Handle the event after command-line arguments are parsed.

        Registers the appropriate assertion rewriter loader based on the parsed arguments.

        :param event: The argument parsed event containing the parsed arguments.
        """
        self._legacy_assertions = event.args.legacy_assertions
        # LegacyAssertRewriterLoader is deprecated and will be removed in v2
        # Since command‑line arguments will no longer be required, this registration
        # can eventually be moved to on_config_loaded
        self._global_config.Registry.ModuleLoader.register(
            # TODO: Make assert_tool configurable
            LegacyAssertRewriterLoader if self._legacy_assertions else AssertRewriterLoader,
            self
        )

        if self._assert_rewrite_paths:
            validated_paths = self._validate_rewrite_paths(self._assert_rewrite_paths,
                                                           self._global_config.project_dir)
            self._register_assert_rewriter(validated_paths)

    def _register_assert_rewriter(self, rewrite_paths: List[Path]) -> None:
        """
        Register assert rewriter finder in sys.meta_path if not already present.

        :param rewrite_paths: List of paths where assertions should be rewritten
        """
        finder = AssertRewriterFinder(rewrite_paths)
        for existing_finder in sys.meta_path:
            if isinstance(existing_finder, AssertRewriterFinder):
                if existing_finder.rewrite_paths == finder.rewrite_paths:
                    return
        sys.meta_path.insert(0, finder)

    def _validate_rewrite_paths(self, paths: RewritePathsType, project_dir: Path) -> List[Path]:
        """
        Validate and resolve rewrite paths relative to project directory.

        :param paths: List of paths to validate
        :param project_dir: Project root directory for resolving relative paths
        :return: List of resolved, validated Path objects
        :raises ValueError: If any path doesn't exist or isn't a directory
        """
        validated_paths = []
        for path_str in paths:
            path = Path(path_str)

            if path.is_absolute():
                resolved_path = path.resolve()
            else:
                resolved_path = (project_dir / path).resolve()

            if not resolved_path.exists():
                raise ValueError(
                    f"Assert rewrite path '{path_str}' does not exist "
                    f"(resolved to '{resolved_path}')"
                )
            if not resolved_path.is_dir():
                raise ValueError(
                    f"Assert rewrite path '{path_str}' is not a directory "
                    f"(resolved to '{resolved_path}')"
                )

            validated_paths.append(resolved_path)

        return validated_paths


class AssertRewriter(PluginConfig):
    """
    Configuration for the AssertRewriterPlugin.

    This configuration allows enabling or disabling the legacy assertion rewriter.
    """

    plugin = AssertRewriterPlugin
    description = "Rewrites assert statements to provide better error messages"

    legacy_assertions: bool = False
    """
    Use legacy assertion rewriter for backwards compatibility.
    """

    assert_rewrite_paths: RewritePathsType = ()
    """
    Paths where assert statements should be rewritten for better error messages.
    Paths are resolved relative to project_dir if not absolute.
    """
