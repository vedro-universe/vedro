import pytest
from baby_steps import given, then, when

from vedro.plugins.functioner._sanitize_identifier import sanitize_identifier


@pytest.mark.parametrize(("identifier", "expected"), [
    # Valid identifier (no change needed)
    ("valid_name", "valid_name"),

    # Python keyword (append underscore)
    ("class", "class_"),

    # Empty input (becomes _ with prefix)
    ("", "scn_"),

    # Starts with digit (prepend underscore + prefix)
    ("123abc", "scn_123abc"),

    # Starts with underscore (add prefix)
    ("_private", "scn_private"),

    # Multiple separator types and consecutive separators (collapse to single underscore)
    ("func--name..test  case", "func_name_test_case"),

    # Invalid characters (removed)
    ("func@name()", "funcname"),

    # Case folding (uppercase to lowercase)
    ("CamelCase", "camelcase"),

    # Unicode special cases (casefold and normalization)
    ("Café_ß", "café_ss"),

    # Truncation (limit to 255 chars)
    ("a" * 300, "a" * 255),

    # Valid unicode identifiers (preserved)
    ("αβγ_变量", "αβγ_变量"),

    # Complex case (multiple rules apply)
    ("@123-CLASS__test!", "scn_123_class_test"),
])
def test_sanitize_identifier(identifier: str, expected: str):
    with given:
        prefix = "scn"

    with when:
        result = sanitize_identifier(identifier, prefix=prefix)

    with then:
        assert result == expected
