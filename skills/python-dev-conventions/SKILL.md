---
name: python-dev-conventions
description: >
  Applies the author's Python conventions while writing code: loguru
  logging with its own config module, code formatted with ruff, and every
  test in one tests/ folder. Use as soon as someone adds or changes Python
  code in a project, adds logging, writes or moves tests, or asks how to
  format or organize Python code, even without naming loguru or ruff. Do
  not use to create a new project (dev-kickoff) or for non-Python code.
metadata:
  author: "Vedasur"
  version: "0.2.0"
  date: "2026-10-30"
---

# Python dev conventions

The author develops in Python with loguru for every log line, formatted code, and one central test folder. Keep these conventions in every change. Creating a new project is the job of the `dev-kickoff` skill: load it instead when there is no project yet.

## Environment: use the project's own

Run every command in the environment the project already uses, because the author chose it at kickoff:

- `compose.yaml` at the root: `docker compose run --rm <service> uv run <command>` (`app`, or `backend` in a frontend and backend app).
- Otherwise: `uv run <command>`.

Add dependencies with `uv add <dep>` (`uv add --dev <dep>` for tooling), in the container when the project uses Docker, so `uv.lock` stays in sync. Never switch the project to the other environment unless the person asks.

## Logging: loguru with its own config module

- Use loguru for all diagnostics; no `print` and no stdlib `logging` in project code.
- All configuration lives in one module that exposes `setup_logging()`: `src/<package>/core/logging_config.py`, or `shared/logging_config.py` in an app with a frontend and a backend. Each entry point (CLI `main`, app startup, script, first notebook cell) calls it once; every other module only does `from loguru import logger`.
- That module sets an explicit color for each level and an explicit date and time format, and routes stdlib logging from third-party libraries into loguru.

Before writing or changing that module, read `references/loguru-config.md`: it holds the house colors, the time format, and the full module.

## Formatting

Code is always formatted with ruff, notebooks included. Configure it in `pyproject.toml` (`[tool.ruff]`, line length 88, `[tool.ruff.lint] select = ["E", "F", "I", "UP", "B"]`) and add it as a dev dependency. After each change, run `ruff format` then `ruff check --fix` in the project's environment. If the commands cannot run, write code that already follows that style and say the formatter was not run.

## Tests

- Every test lives under the top-level `tests/` folder, whose tree mirrors the source (`src/pkg/io/reader.py` is tested in `tests/io/test_reader.py`; `backend/app/services/users.py` in `tests/backend/services/test_users.py`). Never put tests next to the source or inside the package.
- Shared fixtures go in `tests/conftest.py`.
- Declare the folder in `pyproject.toml`: `[tool.pytest.ini_options] testpaths = ["tests"]`, with `addopts = "--import-mode=importlib"` so test files in different folders can share a name.
- Run them with `pytest` in the project's environment.
