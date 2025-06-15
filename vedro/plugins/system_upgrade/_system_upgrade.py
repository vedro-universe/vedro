import json
import platform
import time
import urllib.request
from threading import Thread
from typing import Any, Dict, Tuple, Type, Union, final

from niltype import Nil

import vedro
from vedro.core import Dispatcher, Plugin, PluginConfig
from vedro.core.exp.local_storage import LocalStorageFactory, create_local_storage
from vedro.events import CleanupEvent, ConfigLoadedEvent, StartupEvent

__all__ = ("SystemUpgrade", "SystemUpgradePlugin",)


@final
class SystemUpgradePlugin(Plugin):
    """
    Checks for updates to Vedro and notifies users when a newer version is available.

    This plugin periodically checks for the latest available version of Vedro by
    sending a request to a predefined API endpoint. It compares the current version
    with the latest version and generates a notification if an update is available.
    """

    def __init__(self, config: Type["SystemUpgrade"], *,
                 local_storage_factory: LocalStorageFactory = create_local_storage) -> None:
        """
        Initialize the SystemUpgradePlugin with the given configuration.

        This constructor initializes the plugin with the API URL, request timeout,
        local storage for persisting last request timestamps, and the current version
        of Vedro. It also sets the update check interval.

        :param config: The configuration class for the SystemUpgrade plugin.
        :param local_storage_factory: Factory to create local storage for persisting data.
        """
        super().__init__(config)
        self._api_url = config.api_url
        self._request_timeout = config.api_request_timeout
        self._local_storage_factory = local_storage_factory
        self._thread: Union[Thread, None] = None
        self._latest_version: Union[str, None] = None
        self._last_request_ts: Union[int, None] = None
        self._last_request_error: Union[str, None] = None
        self._cur_version = vedro.__version__
        self._check_interval = config.update_check_interval

    def subscribe(self, dispatcher: Dispatcher) -> None:
        """
        Subscribe to Vedro events to manage update checks and notifications.

        This method registers event listeners for configuration loading, startup,
        and cleanup events to trigger the update check process at appropriate times.

        :param dispatcher: The event dispatcher to register listeners on.
        """
        dispatcher.listen(ConfigLoadedEvent, self.on_config_loaded) \
                  .listen(StartupEvent, self.on_startup) \
                  .listen(CleanupEvent, self.on_cleanup)

    def on_config_loaded(self, event: ConfigLoadedEvent) -> None:
        """
        Handle the configuration loaded event, initializing local storage.

        This method initializes the local storage where the last request timestamp
        is stored, using the provided project directory.

        :param event: The ConfigLoadedEvent containing the loaded configuration.
        """
        self._local_storage = self._local_storage_factory(self, event.config.project_dir)

    async def on_startup(self, event: StartupEvent) -> None:
        """
        Handle the startup event, initiating a background update check if required.

        This method checks the last request timestamp to determine if an update check
        is needed, and if so, starts a background thread to fetch the latest version.

        :param event: The StartupEvent signaling that the system has started.
        """
        last_request = await self._local_storage.get("last_request_ts")
        if (last_request is not Nil) and (last_request + self._check_interval > self._now()):
            return

        self._thread = Thread(target=self._get_latest_version, daemon=True)
        self._thread.start()

    def _is_up_to_date(self, cur_version: str, new_version: str) -> bool:
        """
        Compare the current version with the latest available version.

        This method checks if the current version is up-to-date or newer than
        the latest version available.

        :param cur_version: The current version of Vedro.
        :param new_version: The latest version available from the API.
        :return: True if the current version is up-to-date, False otherwise.
        """
        def parse_version(version: str) -> Tuple[str, ...]:
            return tuple(x.zfill(8) for x in version.split("."))
        return bool(parse_version(cur_version) >= parse_version(new_version))

    async def on_cleanup(self, event: CleanupEvent) -> None:
        """
        Handle the cleanup event, finalizing the update check and persisting data.

        This method ensures that any running background thread for version checking
        is joined and that the last request timestamp and error (if any) are saved.
        It also adds a notification to the test report if an update is available.

        :param event: The CleanupEvent signaling that the system is shutting down.
        """
        if self._thread:
            self._thread.join(0.0)
            self._thread = None

        if self._last_request_ts is None:
            self._last_request_ts = self._now()
            self._last_request_error = f"Request aborted (timeout {self._request_timeout})"

        await self._local_storage.put("last_request_ts", self._last_request_ts)
        await self._local_storage.put("last_request_error", self._last_request_error)
        await self._local_storage.flush()

        if self._latest_version:
            if not self._is_up_to_date(self._cur_version, self._latest_version):
                event.report.add_summary(
                    f"(!) Vedro update available: {self._cur_version} → {self._latest_version}"
                    " | https://vedro.io/changelog"
                )

    def _send_request(self, url: str, *, headers: Dict[str, str], timeout: float) -> Any:
        """
        Send a request to the provided URL and return the JSON response.

        This method sends a GET request to the specified URL with the given headers
        and timeout, and parses the JSON response.

        :param url: The URL to send the request to.
        :param headers: The headers to include in the request.
        :param timeout: The timeout for the request in seconds.
        :return: The parsed JSON response as a Python dictionary.
        """
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read())

    def _get_user_agent(self) -> str:
        """
        Construct the User-Agent string for the HTTP request.

        This method generates a User-Agent string including the current Vedro version,
        Python version, and platform information.

        :return: The User-Agent string.
        """
        python_version = platform.python_version()
        platform_info = platform.platform(terse=True)
        return f"Vedro/{self._cur_version} (Python/{python_version}; {platform_info})"

    def _get_latest_version(self) -> None:
        """
        Fetch the latest available version of Vedro from the API.

        This method sends a request to the API endpoint to fetch the latest version
        of Vedro. If successful, the version is stored, otherwise an error is recorded.
        """
        url = f"{self._api_url}/v1/latest-version"
        headers = {"User-Agent": self._get_user_agent()}
        try:
            response = self._send_request(url, headers=headers, timeout=self._request_timeout)
        except BaseException as e:
            self._last_request_error = str(e)
            self._last_request_ts = self._now()
            return
        if isinstance(response, dict) and ("version" in response):
            self._latest_version = response["version"]
            self._last_request_ts = self._now()

    def _now(self) -> int:
        """
        Get the current time in seconds since the epoch.

        :return: The current Unix timestamp as an integer.
        """
        return int(time.time())


class SystemUpgrade(PluginConfig):
    """
    Configuration class for the SystemUpgradePlugin.

    This class provides configuration options for the SystemUpgradePlugin,
    including the API URL, request timeout, and the interval for checking
    for updates.
    """

    plugin = SystemUpgradePlugin
    description = "Checks for Vedro updates and notifies when a newer version is available"

    # API URL for checking the latest version
    api_url: str = "https://api.vedro.io"

    # Timeout for the API request in seconds
    api_request_timeout: float = 1.0

    # Interval at which the update check should be done, specified in seconds
    update_check_interval: int = 3600 * 16
