import sys
from autofmt.configurations.load_config import load_config
from autofmt.services.logger import log_info
from autofmt.services.watcher import run_watcher


def main() -> None:
    config = load_config()
    log_info("Starting autofmt watcher...")
    log_info(f"At: {config['watch_path']}")
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()
    run_watcher(config)


if __name__ == "__main__":
    main()
