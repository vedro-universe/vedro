from pathlib import Path

__all__ = ("is_relative_to",)


def is_relative_to(path: Path, parent: Path) -> bool:
    """
    Check if the given path is relative to the specified parent directory.

    :param path: The path to check.
    :param parent: The parent directory to check against.
    :return: True if the path is relative to the parent directory, False otherwise.
    """
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    else:
        return path != parent
