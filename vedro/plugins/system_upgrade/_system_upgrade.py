import json
import platform
import time
import urllib.request
from threading import Thread
from typing import Any, Dict, Tuple, Type, Union

from niltype import Nil

import vedro
from vedro.core import Dispatcher, Plugin, PluginConfig
from vedro.core.exp.local_storage import LocalStorageFactory, create_local_storage
from vedro.events import CleanupEvent, StartupEvent

__all__ = ("SystemUpgrade", "SystemUpgradePlugin",)


class SystemUpgradePlugin(Plugin):
    def __init__(self, config: Type["SystemUpgrade"], *,
                 local_storage_factory: LocalStorageFactory = create_local_storage) -> None:
        super().__init__(config)
        self._api_url = config.api_url
        self._request_timeout = config.api_request_timeout
        self._local_storage = local_storage_factory(self)
        self._thread: Union[Thread, None] = None
        self._latest_version: Union[str, None] = None
        self._last_request_ts: Union[int, None] = None
        self._cur_version = vedro.__version__
        self._check_interval = config.update_check_interval

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(StartupEvent, self.on_startup) \
                  .listen(CleanupEvent, self.on_cleanup)

    async def on_startup(self, event: StartupEvent) -> None:
        last_request = await self._local_storage.get("last_request_ts")
        if (last_request is not Nil) and (last_request + self._check_interval > self._now()):
            return

        self._thread = Thread(target=self._get_latest_version, daemon=True)
        self._thread.start()

    def _is_up_to_date(self, cur_version: str, new_version: str) -> bool:
        def parse_version(version: str) -> Tuple[str, ...]:
            return tuple(x.zfill(8) for x in version.split("."))
        return bool(parse_version(cur_version) >= parse_version(new_version))

    async def on_cleanup(self, event: CleanupEvent) -> None:
        if self._thread:
            self._thread.join(0.0)
            self._thread = None

        if self._latest_version is None:
            return

        await self._local_storage.put("last_request_ts", self._last_request_ts)
        await self._local_storage.flush()

        if not self._is_up_to_date(self._cur_version, self._latest_version):
            message = f"(!) Vedro update available: {self._cur_version} → {self._latest_version}"
            event.report.add_summary(message)

    def _send_request(self, url: str, *,
                      headers: Dict[str, str], timeout: float) -> Union[Any, None]:
        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.loads(response.read())
        except BaseException:
            return None

    def _get_user_agent(self) -> str:
        python_version = platform.python_version()
        platform_info = platform.platform(terse=True)
        return f"Vedro/{self._cur_version} (Python/{python_version}; {platform_info})"

    def _get_latest_version(self) -> None:
        url = f"{self._api_url}/v1/latest-version"
        headers = {"User-Agent": self._get_user_agent()}
        response = self._send_request(url, headers=headers, timeout=self._request_timeout)
        if isinstance(response, dict) and ("version" in response):
            self._latest_version = response["version"]
            self._last_request_ts = self._now()

    def _now(self) -> int:
        return int(time.time())


class SystemUpgrade(PluginConfig):
    plugin = SystemUpgradePlugin
    description = "Checks for Vedro updates and notifies when a newer version is available"

    # API URL for checking the latest version
    api_url: str = "https://api.vedro.io"

    # Timeout for the API request in seconds
    api_request_timeout: float = 1.0

    # Interval at which the update check should be done, specified in seconds
    update_check_interval: int = 3600 * 16
