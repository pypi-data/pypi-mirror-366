from os import path
from typing import Any


def get_relative_path(absolute: str, config: dict[str, Any]) -> str:
    """Get the relative path of a file from the watch path specified in the configuration."""
    return path.relpath(absolute, config.get("watch_path", "."))
