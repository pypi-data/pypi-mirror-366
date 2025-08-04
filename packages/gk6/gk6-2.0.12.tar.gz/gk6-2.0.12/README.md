# ⚡ gk6 – Generate k6 Load Tests from Postman Collections

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](/LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Docs](https://img.shields.io/badge/Docs-GitHub%20Pages-blue)](https://gopikrishna4595.github.io/gk6/)

**gk6** is a Python CLI tool that converts Postman collections into dynamic [k6](https://k6.io) performance testing scripts — with support for chaining variables, environment parsing, automated metrics, and HTML reporting. Built to automate what you shouldn’t have to hand-code.

---

## 🎯 Why gk6?

If you use Postman for API testing and k6 for performance testing, this tool connects the dots:

- ✅ No need to rewrite each request manually
- 🔁 It respects your chaining logic (`pm.environment.set`)
- 🌐 Supports environments and headers out of the box
- 📊 Visibility with built-in checks and trend metrics

---

## ✅ Features

- ✅ Converts any Postman Collection to a runnable k6 script
- ✅ Supports `GET`, `POST`, `PUT`, `DELETE` methods
- 🔄 Recognizes and converts environment variables (`{{var}}`)
- 🔁 Detects request chaining via `pm.environment.set()`
- 📊 Auto-generates `Trend` metrics and `check()` assertions
- 🖥 CLI-friendly with `argparse`
- 📄 Optional `.env` and HTML summary output with `k6-reporter`

---

## 🧱 Limitations

* ❗ Currently supports only `pm.environment.set()` for chaining — `pm.variables.set()` is not yet handled.
* ⚠️ Does not parse pre-request scripts or tests written in advanced Postman JavaScript.
* 🔒 Sensitive auth flows (e.g., OAuth2 with token rotation) require manual setup.
* 📄 HTML reporting requires `k6-reporter` installed and configured separately.
* 📦 Limited to JSON-based Postman collections (v2.1+).

---

## 🚀 Quick Start

### 1. Install

No extra packages needed — just Python 3.8+ and [k6](https://k6.io/docs/getting-started/installation)

```bash
pip install poetry
poetry install
```

### 2. Run the CLI

```bash
poetry run gk6 --help
```

Convert a Postman collection and environment:

```bash
poetry run gk6 convert --collection postman.json --env environment.json
```

---

## 🛠 Development

### Local Dev Commands

```bash
make test          # Run unit tests
make lint          # Run all linters
make format        # Apply black, isort formatting
make release       # Bump version and tag release
```

### GitHub Actions

Includes CI for:

* ✅ Linting (black, ruff)
* ✅ Type checking (mypy)
* ✅ Security scan (bandit, detect-secrets)
* ✅ Version bump & release tagging


---

## 🔗 Links

* 📄 [Live Docs on GitHub Pages](https://gopikrishna4595.github.io/gk6/)
* 🐙 [Project Repo](https://github.com/gopikrishna4595/gk6)
* ⚙️ [k6 Docs](https://k6.io/docs/)
* 🧪 [Postman Docs](https://learning.postman.com/docs/)

---

## 📄 License

MIT License — see the [LICENSE](LICENSE) file for full text.
