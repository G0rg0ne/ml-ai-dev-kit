---
name: python-dev-conventions
description: >
  Sets up and maintains Python projects with the author's conventions:
  Docker or uv environment, loguru logging with its own config module,
  formatted code, and tests in one tests/ folder. Use as soon as someone
  starts, scaffolds, or extends a Python project, adds logging, writes
  tests, or asks how to structure Python code, even without naming uv,
  Docker, or loguru. Do not use for non-Python projects or for notebooks
  explored without a project around them.
metadata:
  author: "G0rg0ne"
  version: "0.1.0"
  date: "2026-10-30"
---

# Python dev conventions

The author develops in Python with a reproducible environment, loguru for every log line, formatted code, and one central test folder. Apply these conventions to new projects and keep them in existing ones.

## Environment: ask before creating it

Before writing any environment file (`pyproject.toml`, `uv.lock`, `Dockerfile`, `compose.yaml`), ask once which environment to use, because the author decides it per project:

- **Docker** (the author's usual choice): development runs in a container.
- **uv**: local virtual environment managed by uv.

If the request already says which one, do not ask. If the project already has one (a `Dockerfile` or a `uv.lock`), keep it. Ask the question together with any other missing input, then wait for the answer; do not pick one silently.

Both options use uv for dependencies, so `pyproject.toml` and `uv.lock` are the single source of truth:

- **uv**: `uv init --package <name>` (src layout), `uv add <dep>`, `uv add --dev ruff pytest`, commands through `uv run`.
- **Docker**: the same `pyproject.toml`, plus a `Dockerfile` based on `python:3.12-slim` that copies uv from `ghcr.io/astral-sh/uv` and runs `uv sync --frozen`; a `compose.yaml` that mounts the source for live editing; a `.dockerignore` excluding `.venv`, caches, and `.env`. Commands run through `docker compose run --rm app <command>`.

## Layout

```
<project>/
├── pyproject.toml
├── src/<package>/
│   ├── __init__.py
│   ├── logging_config.py
│   └── ...
└── tests/
    ├── conftest.py
    └── ...
```

## Logging: loguru with its own config module

- Use loguru for all diagnostics; no `print` and no stdlib `logging` in project code.
- All configuration lives in `src/<package>/logging_config.py`, which exposes `setup_logging()`. The entry point (CLI `main`, app startup) calls it once; every other module only does `from loguru import logger`.
- That module sets an explicit color for each level and an explicit date and time format, and routes stdlib logging from third-party libraries into loguru.

Before writing or changing that module, read `references/loguru-config.md`: it holds the house colors, the time format, and the full module.

## Formatting

Code is always formatted with ruff. Configure it in `pyproject.toml` (`[tool.ruff]`, line length 88, `select = ["E", "F", "I", "UP", "B"]`) and add it as a dev dependency. After each change, run `ruff format` then `ruff check --fix` (through `uv run` or the container). If the commands cannot run, write code that already follows that style and say the formatter was not run.

## Tests

- Every test lives under the top-level `tests/` folder, whose tree mirrors `src/<package>/` (`src/pkg/io/reader.py` is tested in `tests/io/test_reader.py`). Never put tests next to the source or inside the package.
- Shared fixtures go in `tests/conftest.py`.
- Declare the folder in `pyproject.toml`: `[tool.pytest.ini_options] testpaths = ["tests"]`.
- Run them with `pytest` through `uv run` or the container.
