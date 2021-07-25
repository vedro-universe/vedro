# Vedro

[![Codecov](https://img.shields.io/codecov/c/github/nikitanovosibirsk/vedro/master.svg?style=flat-square)](https://codecov.io/gh/nikitanovosibirsk/vedro)
[![PyPI](https://img.shields.io/pypi/v/vedro.svg?style=flat-square)](https://pypi.python.org/pypi/vedro/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/vedro?style=flat-square)](https://pypi.python.org/pypi/vedro/)
[![Python Version](https://img.shields.io/pypi/pyversions/vedro.svg?style=flat-square)](https://pypi.python.org/pypi/vedro/)

(!) Work in progress, breaking changes are possible until v2.0 is released

## Installation

```shell
$ pip3 install vedro
```

## Usage

```python
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

```shell
$ python3 -m vedro .
```

## Documentation

* [Documentation](#documentation)
  * [Selecting Scenarios](#selecting-scenarios)
    * [Select File or Directory](#select-file-or-directory)
    * [Skip File or Directory](#skip-file-or-directory)
    * [Select Specific Scenario](#select-specific-scenario)
    * [Skip Specific Scenario](#skip-specific-scenario)
  * [Reporters](#reporters)
    * [Rich Reporter (default)](#rich-reporter-default)
    * [Silent Reporter](#silent-reporter)
  * [Parametrized Scenario](#parametrized-scenario)
  * [Plugins](#plugins)
    * [Register Plugin](#register-plugin)
    * [Available Plugins](#available-plugins)

---

### Selecting Scenarios

#### Select File or Directory

```shell
$ python3 -m vedro <file_or_dir>
```

#### Skip File or Directory

```shell
$ python3 -m vedro -i (--ignore) <file_or_dir>
```

#### Select Specific Scenario

```python
import vedro

@vedro.only
class Scenario(vedro.Scenario):
    subject = "register user"
```

#### Skip Specific Scenario

```python
import vedro

@vedro.skip
class Scenario(vedro.Scenario):
    subject = "register user"
```

### Reporters

#### Rich Reporter (default)

```shell
$ python3 -m vedro -r rich -vvv
```

Verbose Levels

| Verbose | Show Scenario | Show Steps| Show Exception | Show Scope (scenario variables) |
|:--------|:-------------:|:---------:|:--------------:|:----------:|
|      |✅| | | |
|`-v`  |✅|✅| |
|`-vv` |✅|✅|✅| |
|`-vvv`|✅|✅|✅|✅|


#### Silent Reporter

```shell
$ python3 -m vedro -r silent
```

### Parametrized Scenario

```python
from aiohttp import ClientSession
import vedro
from vedro import params

class Scenario(vedro.Scenario):
    subject = "get status ({status})"

    @params(200)
    @params(404)
    def __init__(self, status: int):
        self.status = status

    def given(self):
        self.url = f"https://httpbin.org/status/{self.status}"

    async def when(self):
        async with ClientSession() as session:
            self.response = await session.get(self.url)

    async def then(self):
        assert self.response.status == self.status
```

### Plugins

#### Register Plugin

```python
# ./bootstrap.py
import vedro
from vedro import Dispatcher, Plugin

class DoNothing(Plugin):
    def subscribe(self, dispatcher: Dispatcher) -> None:
        pass

vedro.run(plugins=[DoNothing()])
```

```shell
$ python3 bootstrap.py
```

#### Available Plugins

Core
- [Director](https://github.com/nikitanovosibirsk/vedro/tree/master/vedro/plugins/director)
- [Tagger](https://github.com/nikitanovosibirsk/vedro/tree/master/vedro/plugins/tagger)
- [Skipper](https://github.com/nikitanovosibirsk/vedro/tree/master/vedro/plugins/skipper)
- [Seeder](https://github.com/nikitanovosibirsk/vedro/tree/master/vedro/plugins/seeder)
- [Slicer](https://github.com/nikitanovosibirsk/vedro/tree/master/vedro/plugins/slicer)
- [Interrupter](https://github.com/nikitanovosibirsk/vedro/tree/master/vedro/plugins/interrupter)
- [Deferrer](https://github.com/nikitanovosibirsk/vedro/tree/master/vedro/plugins/deferrer)
- [Terminator](https://github.com/nikitanovosibirsk/vedro/tree/master/vedro/plugins/terminator)

Reporters
- [Rich Reporter](https://github.com/nikitanovosibirsk/vedro/tree/master/vedro/plugins/director/rich)
- [Silent Reporter](https://github.com/nikitanovosibirsk/vedro/tree/master/vedro/plugins/director/silent)
- [GitLab Reporter](https://github.com/nikitanovosibirsk/vedro-gitlab-reporter)
- [Allure Reporter](https://github.com/nikitanovosibirsk/vedro-allure-reporter)

External
- [Valera Validator](https://github.com/nikitanovosibirsk/vedro-valera-validator)

And [more](https://github.com/topics/vedro-plugin)
