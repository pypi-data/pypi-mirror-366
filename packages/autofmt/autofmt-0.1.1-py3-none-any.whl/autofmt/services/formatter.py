import subprocess
import time
from typing import Any

from autofmt.services.logger import log_error, log_success, log_time

last_formatted: dict[str, Any] = {}


def run_formatters(filepath: str, config: dict[str, Any]) -> None:
    cooldown = config.get("cooldown_seconds", 1.0)
    now = time.time()
    if filepath in last_formatted and (now - last_formatted[filepath]) < cooldown:
        return

    time.sleep(0.5)  # Wait for file save to complete
    try:
        result = subprocess.run(
            ["python3", "-m", "py_compile", filepath],
            check=True,
            capture_output=True,
            text=True,
        )
        if result.stdout:
            print(
                f"\n{log_time()} Syntax error logsx:\n  {filepath}\n  {result.stdout.strip()}"
            )

        if "ruff" in config["formatters"]:
            # Run fuff and capture the output
            result = subprocess.run(
                ["ruff", "check", "--fix", filepath],
                check=True,
                capture_output=True,
                text=True,
            )
            if result.stdout:
                print(
                    f"\n{log_time()} Ruff logs:\n  {filepath}\n  {result.stdout.strip()}"
                )
        if "black" in config["formatters"]:
            # Run black and capture the output
            result = subprocess.run(
                ["black", filepath],
                check=True,
                capture_output=True,
                text=True,
            )
            if result.stdout:
                print(
                    f"\n{log_time()} Black logs:\n  {filepath}\n  {result.stdout.strip()}"
                )
        last_formatted[filepath] = now
        log_success(f"\n{log_time()} Formatted path:\n  {filepath}")
    except subprocess.CalledProcessError:
        log_error(
            f"\n{log_time()} Syntax error logs:\n  {filepath}\n  skipping formatting."
        )
