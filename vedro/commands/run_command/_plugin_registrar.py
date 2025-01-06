from collections import defaultdict, deque
from typing import Callable, Dict, Iterable, List, Type, Union

from vedro.core import Dispatcher, PluginConfig

from ._plugin_config_validator import PluginConfigValidator

__all__ = ("PluginRegistrar",)

PluginConfigValidatorFactory = Union[
    Type[PluginConfigValidator],
    Callable[[], PluginConfigValidator]
]


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
        Retrieve an ordered list of enabled plugins based on their dependencies.

        This method first validates plugins, filters enabled plugins,
        and then orders them using topological sorting.

        :param plugins: An iterable of plugin configuration classes.
        :return: A list of plugin configuration classes in topological order.
        """
        available_plugins = set(plugins)

        enabled_plugins = []
        for plugin_config in plugins:
            self._plugin_config_validator.validate(plugin_config, available_plugins)
            if plugin_config.enabled:
                enabled_plugins.append(plugin_config)

        return self._order_plugins(enabled_plugins)

    def _order_plugins(self, plugins: List[Type[PluginConfig]]) -> List[Type[PluginConfig]]:
        """
        Order the given plugins based on their dependencies using a topological sort.

        This method ensures that plugins are loaded in an order that respects their
        dependencies, raising an error if a cyclic dependency is detected.

        :param plugins: A list of plugin configuration classes.
        :return: A list of plugin configuration classes in topological order.
        :raises RuntimeError: If a cycle is detected in the plugin dependencies.
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
                adjacency[dep].append(plugin)
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
            raise RuntimeError("Cycle detected in plugin dependencies")

        return ordered
