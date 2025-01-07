from collections import defaultdict, deque
from os import linesep
from typing import Callable, Dict, Iterable, List, Type, Union

from vedro.core import Dispatcher, PluginConfig

from ._plugin_config_validator import PluginConfigValidator

__all__ = ("PluginRegistrar",)

PluginConfigValidatorFactory = Union[
    Type[PluginConfigValidator],
    Callable[[], PluginConfigValidator]
]

ResolvedDeps = Dict[Type[PluginConfig], Type[PluginConfig]]


class PluginRegistrar:
    """
    Manages the registration of plugins and ensures their dependencies are satisfied.

    This class validates plugins, resolves their dependencies, orders them
    topologically, and registers them with the provided dispatcher.
    """

    def __init__(self, *,
                 plugin_config_validator_factory: PluginConfigValidatorFactory =
                 PluginConfigValidator) -> None:
        """
        Initialize the PluginRegistrar.

        :param plugin_config_validator_factory: Factory for creating a `PluginConfigValidator`
                                                instance, used to validate plugin configurations.
        """
        self._plugin_config_validator = plugin_config_validator_factory()

    def register(self, plugins: Iterable[Type[PluginConfig]], dispatcher: Dispatcher) -> None:
        """
        Register plugins with the dispatcher.

        This method validates, orders, and registers enabled plugins with the dispatcher.

        :param plugins: An iterable of plugin configuration classes.
        :param dispatcher: The dispatcher to which the plugins will be registered.
        """
        for plugin_config in self._get_ordered_plugins(plugins):
            plugin = plugin_config.plugin(config=plugin_config)
            dispatcher.register(plugin)

    def _get_ordered_plugins(self,
                             plugins: Iterable[Type[PluginConfig]]) -> List[Type[PluginConfig]]:
        """
        Get a topologically ordered list of enabled plugins.

        This method validates each plugin, filters out disabled plugins, resolves their
        dependencies, and returns them in a dependency-respecting order.

        :param plugins: An iterable of plugin configuration classes.
        :return: A list of enabled plugin configuration classes in topological order.
        """
        enabled_plugins = []
        for plugin_config in plugins:
            self._plugin_config_validator.validate(plugin_config)
            if plugin_config.enabled:
                enabled_plugins.append(plugin_config)

        return self._order_plugins(enabled_plugins, self._resolve_dependencies(plugins))

    def _resolve_dependencies(self, plugins: Iterable[Type[PluginConfig]]) -> ResolvedDeps:
        """
        Resolve dependencies between plugins.

        This method maps each plugin to its dependencies, ensuring that they are satisfied
        and enabled.

        :param plugins: An iterable of plugin configuration classes.
        :return: A dictionary mapping plugin configuration classes to their resolved dependencies.
        :raises ValueError: If a plugin depends on an unknown or disabled plugin.
        """
        resolved_deps = {plugin: plugin for plugin in plugins}

        for plugin in plugins:
            for dep in plugin.depends_on:
                resolved = self._resolve_dependency(dep, resolved_deps)

                if resolved is None:
                    raise ValueError(
                        f"Plugin '{plugin.__name__}' depends on unknown plugin '{dep.__name__}'"
                    )

                if not resolved.enabled:
                    raise ValueError(
                        f"Plugin '{plugin.__name__}' depends on disabled plugin '{dep.__name__}'"
                    )

                resolved_deps[dep] = resolved

        return resolved_deps

    def _resolve_dependency(self, dep: Type[PluginConfig],
                            resolved_deps: ResolvedDeps) -> Union[Type[PluginConfig], None]:
        """
        Resolve a single dependency.

        This method attempts to find a match for the dependency in the resolved dependencies.

        :param dep: The plugin configuration class to resolve.
        :param resolved_deps: A dictionary of already resolved dependencies.
        :return: The resolved plugin configuration class if found, or `None` if not found.
        """
        if dep in resolved_deps:
            return dep

        for candidate in resolved_deps:
            if (candidate.__name__ == dep.__name__) and issubclass(candidate.plugin, dep.plugin):
                return candidate

        return None

    def _order_plugins(self, plugins: List[Type[PluginConfig]],
                       resolved_deps: ResolvedDeps) -> List[Type[PluginConfig]]:
        """
        Order the given plugins based on their dependencies using a topological sort.

        This method ensures that plugins are loaded in an order that respects their
        dependencies, raising an error if a cyclic dependency is detected.

        :param plugins: A list of enabled plugin configuration classes.
        :param resolved_deps: A dictionary mapping plugins to their resolved dependencies.
        :return: A list of plugin configuration classes in topological order.
        :raises RuntimeError: If a cyclic dependency is detected between plugins.
        """
        # adjacency will map each plugin to the list of plugins that depend on it
        adjacency: Dict[Type[PluginConfig], List[Type[PluginConfig]]] = defaultdict(list)
        # in_degree keeps track of how many direct dependencies each plugin has
        in_degree: Dict[Type[PluginConfig], int] = defaultdict(int)

        # First, build the adjacency list and in_degree map.
        # For each plugin:
        # - Ensure it's represented in in_degree (defaulting to 0).
        # - For each dependency, add this plugin to the dependency's adjacency list,
        #   and increment this plugin's in_degree.
        for plugin in plugins:
            in_degree[plugin] = in_degree.get(plugin, 0)
            for dep in plugin.depends_on:
                resolved = resolved_deps[dep]
                adjacency[resolved].append(plugin)
                in_degree[plugin] += 1

        # Initialize a queue with all plugins that have an in_degree of 0,
        # meaning they have no dependencies or all of their dependencies
        # are not in the enabled plugin list.
        queue = deque([p for p in plugins if in_degree[p] == 0])

        # We'll store our ordered result in 'ordered',
        # and track the count of visited plugins in 'visited_count'
        ordered = []
        visited_count = 0

        # Standard topological sort process:
        # Remove a plugin from the queue, add it to the result list,
        # then decrement the in_degree of all its "neighbors" (plugins that depend on it).
        # If a neighbor's in_degree drops to 0, add it to the queue.
        while queue:
            plugin = queue.popleft()
            ordered.append(plugin)
            visited_count += 1

            for neighbor in adjacency[plugin]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # If the number of visited plugins doesn't match
        # the total number of plugins, we have a cycle.
        if visited_count != len(plugins):
            problematic_plugins = [p.__name__ for p, deg in in_degree.items() if deg > 0]
            bullet_prefix = f"{linesep}  - "
            raise RuntimeError(
                "A cyclic dependency between plugins has been detected. "
                "Any of the following plugins could be referencing each other in a cycle:"
                f"{bullet_prefix + bullet_prefix.join(problematic_plugins)}{linesep}"
                "Please review their 'depends_on' references to resolve this issue."
            )

        return ordered
