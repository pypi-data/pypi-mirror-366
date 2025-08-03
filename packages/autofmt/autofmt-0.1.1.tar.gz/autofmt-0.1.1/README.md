# 🧼 autofmt

A lightweight, extensible, and colorful CLI tool for automatically formatting Python files using **Black** and **Ruff**, triggered by real-time file changes via **Watchdog**. Ideal for developers who want instant feedback, enforced formatting, and smoother workflows.

## 🚀 Features

* 🎯 Watches `.py` files in real time
* 🧹 Auto-formats using **Black** and **Ruff**
* 🧠 Runs Python syntax checks before formatting
* 🎨 Beautiful, structured logs with **Rich**
* 🔧 Supports user-defined config via `pyproject.toml`
* 📂 Designed for easy integration and extension

## 📦 Installation

Install using your preferred Python package manager:

### With `uv`

```bash
uv add autofmt
````

### With `pip`

```bash
pip install autofmt
```

## ⚙️ Configuration

Configure behavior directly in your `pyproject.toml` under `[tool.autofmt]`:

```toml
[tool.autofmt]
watch_path = "."                 # Directory to watch
formatters = ["black", "ruff"]   # Tools to use
cooldown_seconds = 1.0           # Cooldown between re-runstrue)
```

## 🧠 Usage

### Start the watcher

```bash
autofmt
```

It will:

1. Watch for changes in Python files.
2. Run syntax checks.
3. Auto-format using Ruff and Black.
4. Show you real-time logs and success/error messages.

## 📁 Example Output

```bash
starting autofmt watcher...
At: .

Detected change:
  src/autofmt/configurations/load_config.py

Ruff logs:
  src/autofmt/configurations/load_config.py
  All checks passed!

Formatted path:
  src/autofmt/configurations/load_config.py

Detected change:
  src/autofmt/configurations/load_config.py

Detected change:
  src/autofmt/configurations/load_config.py
^C
Stopping watcher...

```

## ❗ Requirements

* Python `>=3.13`
* OS Independent

---

## 🧪 Testing

Run tests using:

```bash
pytest
```

## 🛠️ Planned Features

* 🧩 Plugin support for more formatters
* 🧪 Test coverage reporting
* 📊 Per-file formatter summary
* ⌨️ Command-line flags (e.g., `--path`)
* 📁 Multi-folder watch support

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repo
2. Create a branch
3. Submit a PR
4. Discuss features in the [issues](https://github.com/shaileshpandit141/autofmt/issues)

## 📄 License

MIT License. See the [LICENSE](LICENSE) file for full details.

## 👤 Author

For questions or assistance, contact **Shailesh** at [shaileshpandit141@gmail.com](mailto:shaileshpandit141@gmail.com)
