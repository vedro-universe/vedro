import json
import platform
import urllib.request
from threading import Thread
from typing import Any, Dict, Tuple, Type, Union

import vedro
from vedro.core import Dispatcher, Plugin, PluginConfig
from vedro.events import CleanupEvent, StartupEvent

__all__ = ("SystemUpgrade", "SystemUpgradePlugin",)


class SystemUpgradePlugin(Plugin):
    def __init__(self, config: Type["SystemUpgrade"]) -> None:
        super().__init__(config)
        self._api_url = config.api_url
        self._timeout = config.timeout
        self._thread: Union[Thread, None] = None
        self._latest_version: Union[str, None] = None
        self._cur_version = vedro.__version__

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(StartupEvent, self.on_startup) \
                  .listen(CleanupEvent, self.on_cleanup)

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
        url = f"{self._api_url}/v1/last-version"
        headers = {"User-Agent": self._get_user_agent()}
        response = self._send_request(url, headers=headers, timeout=self._timeout)
        if isinstance(response, dict) and ("version" in response):
            self._latest_version = response["version"]

    def on_startup(self, event: StartupEvent) -> None:
        self._thread = Thread(target=self._get_latest_version, daemon=True)
        self._thread.start()

    def _is_up_to_date(self, cur_version: str, new_version: str) -> bool:
        try:
            from pkg_resources import parse_version  # type: ignore
        except ImportError:
            def parse_version(version: str) -> Tuple[str, ...]:
                return tuple(x.zfill(8) for x in version.split("."))
        return bool(parse_version(cur_version) >= parse_version(new_version))

    def on_cleanup(self, event: CleanupEvent) -> None:
        if self._thread:
            self._thread.join(0.0)
            self._thread = None

        if self._latest_version is None:
            return

        if not self._is_up_to_date(self._cur_version, self._latest_version):
            message = f"(!) Vedro update available: {self._cur_version} → {self._latest_version}"
            event.report.add_summary(message)


class SystemUpgrade(PluginConfig):
    plugin = SystemUpgradePlugin

    # URL to the Vedro API
    api_url: str = "https://api.vedro.io"

    # Timeout for the request to the API
    timeout: float = 1.0
