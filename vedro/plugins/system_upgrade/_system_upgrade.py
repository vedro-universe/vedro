import json
import urllib.request
from threading import Thread
from typing import Any, Dict, Type, Union

import vedro
from vedro.core import Dispatcher, Plugin, PluginConfig
from vedro.events import CleanupEvent, StartupEvent

__all__ = ("SystemUpgrade", "SystemUpgradePlugin",)


class SystemUpgradePlugin(Plugin):
    def __init__(self, config: Type["SystemUpgrade"]) -> None:
        super().__init__(config)
        self._api_url = config.api_url
        self._timeout = 1.0
        self._thread: Union[Thread, None] = None
        self._latest_version: Union[str, None] = None
        self._cur_version = vedro.__version__
        self._cur_version = "1.7.1"  # debug

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

    def _get_latest_version(self) -> None:
        url = f"{self._api_url}/v1/last-version"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = self._send_request(url, headers=headers, timeout=self._timeout)
        if isinstance(response, dict) and ("version" in response):
            self._latest_version = response["version"]

    def on_startup(self, event: StartupEvent) -> None:
        self._thread = Thread(target=self._get_latest_version, daemon=True)
        self._thread.start()

    def on_cleanup(self, event: CleanupEvent) -> None:
        if self._thread:
            self._thread.join(0.0)
            self._thread = None

        if self._latest_version and (self._latest_version != self._cur_version):
            event.report.add_summary(
                f"(!) Vedro update available: {self._cur_version} → {self._latest_version}")


class SystemUpgrade(PluginConfig):
    plugin = SystemUpgradePlugin

    api_url: str = "https://api.vedro.io"
