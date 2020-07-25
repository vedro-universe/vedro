# Vedro

[![Codecov](https://img.shields.io/codecov/c/github/nikitanovosibirsk/vedro/master.svg?style=flat-square)](https://codecov.io/gh/nikitanovosibirsk/vedro)
[![PyPI](https://img.shields.io/pypi/v/vedro.svg?style=flat-square)](https://pypi.python.org/pypi/vedro/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/vedro?style=flat-square)](https://pypi.python.org/pypi/vedro/)
[![Python Version](https://img.shields.io/pypi/pyversions/vedro.svg?style=flat-square)](https://pypi.python.org/pypi/vedro/)

(!) Work in progress, breaking changes are possible until v2.0 is released

## Installation

```sh
pip3 install vedro
```

## Usage

```python3
# ./scenarios/decode_base64_encoded_string.py
from aiohttp import ClientSession
import vedro


class Scenario(vedro.Scenario):
    subject = "decode base64 encoded string"

    def given(self):
        self.encoded = "YmFuYW5h"

    async def when(self):
        async with ClientSession() as session:
            self.response = await session.get(f"https://httpbin.org/base64/{self.encoded}")

    async def then(self):
        assert (await self.response.text()) == "banana"
```

```sh
python3 -c "import vedro; vedro.run()"
```
