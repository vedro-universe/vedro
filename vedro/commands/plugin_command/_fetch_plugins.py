import json
import platform
import urllib.request
from typing import Dict, List, cast

import vedro

__all__ = ("fetch_top_plugins",)


async def fetch_top_plugins(limit: int, timeout: float, *,
                            api_url: str = "https://api.vedro.io/v1") -> List[Dict[str, str]]:
    url = api_url + f"/plugins/top?limit={limit}"
    headers = {"User-Agent": _get_user_agent()}
    plugins = _send_request(url, headers=headers, timeout=timeout)
    return plugins


def _send_request(url: str, *, headers: Dict[str, str], timeout: float) -> List[Dict[str, str]]:
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        result = json.loads(response.read())
    return cast(List[Dict[str, str]], result)


def _get_user_agent() -> str:
    python_version = platform.python_version()
    platform_info = platform.platform(terse=True)
    return f"Vedro/{vedro.__version__} (Python/{python_version}; {platform_info})"
