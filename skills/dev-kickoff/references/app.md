# App: frontend and backend

FastAPI backend and Streamlit frontend in one repository, sharing one `pyproject.toml`, one `uv.lock`, and one `tests/` folder. The project is not an installable package: modules import from the repository root (`backend.app.main`, `shared.logging_config`).

## Tree

```
<project>/
├── backend/
│   ├── __init__.py
│   └── app/
│       ├── __init__.py
│       ├── main.py                 # FastAPI app, calls setup_logging(), includes routers
│       ├── api/
│       │   ├── __init__.py
│       │   ├── deps.py             # dependency providers (settings, db session)
│       │   └── v1/
│       │       ├── __init__.py
│       │       ├── router.py       # api_router, includes every category router
│       │       └── endpoints/
│       │           ├── __init__.py
│       │           └── health/
│       │               ├── __init__.py       # router with prefix /health
│       │               └── get_status.py     # GET /api/v1/health/get_status -> {"status": "ok"}
│       ├── core/
│       │   ├── __init__.py
│       │   └── config.py           # backend settings, from .env
│       ├── db/__init__.py
│       ├── models/__init__.py
│       ├── schemas/__init__.py
│       └── services/__init__.py
├── frontend/
│   ├── __init__.py
│   ├── app.py                      # Streamlit home page, calls setup_logging()
│   ├── pages/.gitkeep
│   ├── components/__init__.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── api_client.py           # only place that calls the backend, base URL from BACKEND_URL
│   ├── utils/__init__.py
│   └── .streamlit/config.toml
├── shared/
│   ├── __init__.py
│   └── logging_config.py           # used by backend and frontend
├── tests/
│   ├── conftest.py
│   ├── backend/test_health.py      # TestClient on /api/v1/health
│   ├── frontend/.gitkeep
│   └── shared/.gitkeep
├── pyproject.toml
├── README.md
├── DEVELOPMENT.md
├── .env.example                    # BACKEND_URL, LOG_LEVEL, CORS_ORIGINS
└── .gitignore
```

The backend allows CORS from the frontend origin (`http://localhost:8501` by default, from `CORS_ORIGINS`). The backend files (routers, settings, `.env.example`, the drift test `tests/core/test_env_example.py`) follow the `fastapi-backend` skill: load it before writing them.

## pyproject.toml

```toml
[project]
name = "<project>"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["loguru", "pydantic-settings", "python-dotenv"]

[dependency-groups]
backend = ["fastapi", "uvicorn[standard]"]
frontend = ["streamlit", "requests"]
dev = ["ruff", "pytest", "httpx"]

[tool.uv]
package = false
default-groups = "all"

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
addopts = "--import-mode=importlib"
```

`--import-mode=importlib` lets two test files share a name in different folders, and keeps `tests/backend/` from shadowing the `backend` package.

## Commands (uv)

```
uv sync
uv run uvicorn backend.app.main:app --reload
uv run streamlit run frontend/app.py
uv run pytest
```

Backend on http://localhost:8000 (docs at `/docs`), frontend on http://localhost:8501.
