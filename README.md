# Vedro

(!) Work in progress, breaking changes are possible until v2.0 is released

## Installation

```sh
pip3 install vedro
```

## Usage

```python3
# ./scenarios/decode_base64_encoded_string.py
import aiohttp
import vedro


class Scenario(vedro.Scenario):
    subject = "decode base64 encoded string"

    def given(self):
        self.encoded = "YmFuYW5h"

    async def when(self):
        async with aiohttp.ClientSession() as session:
            self.response = await session.get(f"https://httpbin.org/base64/{self.encoded}")

    async def then(self):
        assert (await self.response.text()) == "banana"
```

```sh
python3 -c "import vedro; vedro.run()"
```
