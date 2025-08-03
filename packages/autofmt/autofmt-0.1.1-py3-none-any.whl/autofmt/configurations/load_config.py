import tomllib
from typing import Any


def load_config() -> dict[str, Any]:
    """Load the configuration from pyproject.toml."""
    default = {
        "watch_path": ".",
        "formatters": ["black", "ruff"],
        "cooldown_seconds": 1.0,
    }
    try:
        with open("pyproject.toml", "rb") as f:
            pyproject = tomllib.load(f)
            return {
                **default,
                **pyproject.get("tool", {}).get("autofmt", {}),
            }
    except FileNotFoundError:
        return default
