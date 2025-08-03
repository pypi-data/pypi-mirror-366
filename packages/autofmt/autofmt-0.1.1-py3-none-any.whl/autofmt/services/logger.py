from datetime import datetime

from rich.console import Console

# Create a console instance for logging
console = Console()


def log_info(msg: str) -> None:
    """Logs an informational message to the console."""
    console.print(f"[blue]{msg}[/blue]")


def log_success(msg: str) -> None:
    """Logs a success message to the console."""
    console.print(f"[green]{msg}[/green]")


def log_error(msg: str) -> None:
    """Logs an error message to the console."""
    console.print(f"[red]{msg}[/red]")


def log_warn(msg: str) -> None:
    """Logs a warning message to the console."""
    console.print(f"[yellow]{msg}[/yellow]")


def log_time() -> str:
    now = datetime.now()
    return f"{now.strftime('%H:%M:%S')}"
