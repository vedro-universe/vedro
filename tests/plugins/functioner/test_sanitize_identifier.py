import pytest
from baby_steps import given, then, when

from vedro.plugins.functioner._sanitize_identifier import sanitize_identifier


@pytest.mark.parametrize(("identifier", "expected"), [
    # Already valid identifiers (no change)
    ("func", "func"),
    ("valid_identifier", "valid_identifier"),

    # Python keywords (append underscore)
    ("def", "def_"),
    ("class", "class_"),

    # Empty/whitespace only (becomes _ with prefix)
    ("", "scn_"),
    ("   ", "scn_"),

    # Starts with digit (prepend underscore + prefix)
    ("123", "scn_123"),
    ("1func", "scn_1func"),

    # Starts with underscore (add prefix)
    ("_private", "scn_private"),
    ("__init__", "scn__init__"),

    # Contains separators (replace with underscore)
    ("func-name", "func_name"),
    ("func.name", "func_name"),
    ("func name", "func_name"),

    # Contains invalid characters (remove them)
    ("func@name", "funcname"),
    ("func()", "func"),

    # Only invalid characters (becomes _ with prefix)
    ("###", "scn_"),

    # Consecutive separators (multiple underscores)
    ("func--name", "func_name"),
    ("func  name", "func_name"),

    # Case preservation
    ("CamelCase", "CamelCase"),
    ("SCREAMING_SNAKE", "SCREAMING_SNAKE"),

    # Complex combination (multiple rules apply)
    ("123-abc!", "scn_123_abc"),
    ("@class.method()", "class_method"),
])
def test_sanitize_identifier(identifier: str, expected: str):
    with given:
        prefix = "scn"

    with when:
        result = sanitize_identifier(identifier, prefix=prefix)

    with then:
        assert result == expected
