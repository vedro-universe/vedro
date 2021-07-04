# Skipper Plugin

## Selecting Scenarios

### Select File or Directory

```shell
$ python3 -m vedro <file_or_dir>
```

### Skip File or Directory

```shell
$ python3 -m vedro -i (--ignore) <file_or_dir>
```

### Select Specific Scenario

```python
import vedro

@vedro.only
class Scenario(vedro.Scenario):
    subject = "register user"
```

### Skip Specific Scenario

```python
import vedro

@vedro.skip
class Scenario(vedro.Scenario):
    subject = "register user"
```
