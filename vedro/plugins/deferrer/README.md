# Deferrer Plugin

## Usage

```python
# ./contexts/created_session.py
from aiohttp import ClientSession
import vedro

@vedro.context
def created_session() -> ClientSession:
    session = ClientSession()
    vedro.defer(session.close)
    return session
```

```python
# ./scenarios/decode_base64_encoded_string.py
import vedro
from contexts import created_session

class Scenario(vedro.Scenario):
    subject = "decode base64 encoded string"

    def given_session(self):
        self.session = created_session()

    def given_encoded(self):
        self.encoded = "YmFuYW5h"

    async def when_user_decodes_str(self):
        self.response = await self.session.get(f"https://httpbin.org/base64/{self.encoded}")

    async def then_it_should_return_decoded_str(self):
        assert (await self.response.text()) == "banana"
```

```shell
$ vedro run
```
