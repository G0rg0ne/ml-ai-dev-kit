# Service: a backend on its own

An API, a worker, or a CLI, as an installable package in a `src/` layout. When the service exposes HTTP, load the `fastapi-backend` skill and add its `api/` layer (category routers, `health/get_status.py`), FastAPI and uvicorn as dependencies, and the drift test `tests/core/test_env_example.py`; `main.py` then holds the FastAPI app.

## Tree

```
<project>/
├── src/<package>/
│   ├── __init__.py
│   ├── main.py                 # entry point: setup_logging(), load settings, start
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # settings from the environment
│   │   └── logging_config.py
│   ├── schemas/__init__.py     # data shapes exchanged in and out
│   ├── services/__init__.py    # business logic, no I/O details
│   └── adapters/__init__.py    # databases, HTTP clients, queues, storage
├── tests/
│   ├── conftest.py
│   └── core/test_config.py     # settings load with defaults
├── pyproject.toml
├── README.md
├── DEVELOPMENT.md
├── .env.example                # LOG_LEVEL and the service's settings
└── .gitignore
```

Dependencies point inward: `services/` may import `schemas/` and `core/`, and receives adapters as arguments; `adapters/` never imports `services/`.

## pyproject.toml

```toml
[project]
name = "<project>"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["loguru", "pydantic-settings", "python-dotenv"]

[project.scripts]
<project> = "<package>.main:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[dependency-groups]
dev = ["ruff", "pytest"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--import-mode=importlib"
```

## Commands (uv)

```
uv sync
uv run <project>
uv run pytest
```
