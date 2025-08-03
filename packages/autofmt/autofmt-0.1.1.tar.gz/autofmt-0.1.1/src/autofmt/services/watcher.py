import os
import sys
import time
from typing import Any

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer
from watchdog.observers.api import BaseObserver

from autofmt.services.formatter import run_formatters
from autofmt.services.get_relative_path import get_relative_path
from autofmt.services.logger import log_info, log_time


class FormatHandler(FileSystemEventHandler):
    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__()
        self.config = config

    def on_modified(self, event: FileSystemEvent) -> None:
        global privious_path
        if event.is_directory or not event.src_path.endswith(".py"):
            return
        filepath = os.path.abspath(event.src_path)
        relative_path = get_relative_path(filepath, self.config)
        log_info(f"\n{log_time()} Detected change:\n  {relative_path}")
        run_formatters(relative_path, self.config)


def run_watcher(config: dict[str, Any]) -> None:
    path: str = config.get("watch_path", ".")
    event_handler: FormatHandler = FormatHandler(config)
    observer: BaseObserver = Observer()
    observer.schedule(event_handler, path=path, recursive=True)  # type: ignore
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        log_info("\nStopping watcher...")
        sys.stdout.write("\033[?25h\r")
    observer.join()
