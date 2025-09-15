import keyword
import re
import unicodedata
from typing import List

__all__ = ("sanitize_identifier",)


def sanitize_identifier(s: str, *, prefix: str = "fn") -> str:
    """
    Convert a string into a valid Python identifier.

    The function replaces invalid characters, ensures compliance with Python's
    identifier rules, avoids reserved keywords, and adds a prefix if the result
    begins with an underscore. Unicode characters that are valid in Python
    identifiers are preserved.

    :param s: The input string to sanitize into a Python identifier.
    :param prefix: The prefix to prepend if the identifier starts with an underscore.
                   Defaults to "fn".
    :return: A valid Python identifier as a string.
    """
    # Normalize Unicode to NFC (Canonical Decomposition, followed by Canonical Composition)
    # This ensures consistent representation of accented characters and similar Unicode variants
    s = unicodedata.normalize("NFC", str(s))

    # Convert to lowercase using Unicode-aware case folding
    # This handles special cases like German ß → ss more correctly than lower()
    s = s.casefold()

    # Replace common separators with underscores
    s = re.sub(r'[\s\-\.]+', '_', s)

    # Build identifier character by character
    result: List[str] = []
    for char in s:
        if result:
            # For subsequent characters, test if adding it keeps it valid
            test = ''.join(result) + char
            if test.isidentifier():
                result.append(char)
        else:
            # For first character
            if char.isidentifier():
                result.append(char)
            elif ('_' + char).isidentifier():
                result.append('_')
                result.append(char)

    # Join the validated characters into a string
    # At this point, we have a syntactically valid identifier (or empty string)
    s = ''.join(result)

    # Clean up multiple consecutive underscores and remove trailing underscores only
    # This improves readability while preserving leading underscores if present
    s = re.sub(r"_+", "_", s).rstrip("_")

    # If string is empty after cleaning, use underscore
    if not s:
        s = "_"

    # Make sure it's not a Python keyword
    if keyword.iskeyword(s):
        s = s + "_"

    # Add prefix if starts with underscore
    if s.startswith("_") and prefix:
        s = prefix + s

    # Truncate to 255 characters to ensure reasonable identifier length
    # This prevents excessively long identifiers that could cause issues in some contexts
    return s[:255]
