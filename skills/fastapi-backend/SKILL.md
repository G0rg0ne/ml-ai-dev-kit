---
name: fastapi-backend
description: >
  Builds and extends Python backends with FastAPI: endpoints, routers per
  category, Pydantic request and response schemas, services, and settings
  read from .env. Use as soon as someone adds, changes, or reviews an API
  endpoint, route, request validation, or backend configuration, even
  without naming FastAPI. Do not use for frontend pages or for creating a
  new project from scratch (dev-kickoff).
metadata:
  author: "G0rg0ne"
  version: "0.1.0"
  date: "2026-10-30"
---

# FastAPI backend

Every HTTP backend uses FastAPI, validates what comes in and goes out with Pydantic, and groups endpoints by category so new categories (`/payment/...`, `/model/...`) plug in without touching the others. Load `python-dev-conventions` too: logging, formatting, and tests follow it.

`<root>` below is the backend's import root: `backend.app` in an app with a frontend, `<package>` in a standalone service.

## Routing: one file per endpoint, one router per category

```
<root>/api/
├── deps.py                     # shared dependencies (settings, services, db session)
└── v1/
    ├── router.py               # api_router: includes every category router
    └── endpoints/
        ├── payment/
        │   ├── __init__.py     # router = APIRouter(prefix="/payment", tags=["payment"])
        │   ├── get_user.py     # GET  /api/v1/payment/get_user
        │   └── create_payment.py
        └── model/
            ├── __init__.py     # router = APIRouter(prefix="/model", tags=["model"])
            └── get_available_models.py
```

- **Each endpoint is its own file** that defines `router = APIRouter()` and exactly one route. The file name is the last path segment (`get_user.py` serves `/get_user`), unless the person asks for another path.
- **Each category is a package** whose `__init__.py` creates the category router with its `prefix` and `tags` and includes every endpoint router of the folder.
- **`api/v1/router.py`** includes every category router; `main.py` includes `api_router` once, with the prefix from settings (`/api/v1`). Adding a category means a new folder plus one line in `router.py`.
- An endpoint stays thin: it receives validated input, calls a service from `<root>/services/<category>.py` through a dependency, maps domain errors to `HTTPException`, and returns a response schema. No business logic, no database or HTTP client calls, no settings lookups in the endpoint file.

## Validation: Pydantic schemas for every request and response

- Schemas live in `<root>/schemas/<category>.py`, named `<Action>Request` and `<Thing>Response` (or the domain noun).
- Request bodies are Pydantic models with `model_config = ConfigDict(extra="forbid")` and constraints on the fields (`Field(gt=0)`, `pattern`, `max_length`, enums with `Literal`), so malformed input is rejected with a 422 before the endpoint runs.
- Query parameters with more than one field also go in a model, read with `Annotated[Model, Query()]`; a single path or query value uses `Annotated[int, Query(gt=0)]`.
- Every route declares `response_model` (or a return annotation with a schema), so the output is validated and documented in `/docs`; never return raw dicts or ORM objects.

## Settings: every variable in .env, mirrored in .env.example

- All configuration comes from environment variables, loaded from `.env` by one `Settings` class (pydantic-settings) in `<root>/core/config.py`, exposed through a cached `get_settings()` and injected with `Depends`. No `os.getenv`, and no hard-coded URLs, keys, ports, timeouts, limits, or CORS origins anywhere else.
- Secrets are `SecretStr` without a default, so a missing key fails at startup instead of at the first request.
- `.env` is never committed and never shown with real values. `.env.example` lists every setting, grouped by category with a comment, with a safe default or a `change-me` placeholder.
- **Each time a setting is added, renamed, or removed**, update `Settings` and `.env.example` in the same change, then end the answer with the full updated `.env.example` in a code block and a line telling the person which keys to add to their own `.env`.
- The project keeps the test `tests/core/test_env_example.py`, which fails when `Settings` and `.env.example` drift apart.

Before writing an endpoint, a category, or settings, read `references/endpoint-pattern.md` for the full code of each file, and `references/settings.md` for `config.py`, `.env.example`, and the drift test.

## Tests

Each endpoint has a test file mirroring it (`tests/api/v1/payment/test_get_user.py`) that calls it through `TestClient`, replaces services with fakes via `app.dependency_overrides`, and covers one success and one rejected input (422).

## Done when

- The endpoint file, its category router registration, its schemas, its service method, and its test exist.
- `.env.example` matches `Settings`, and the answer shows it if a setting changed.
- Format and tests ran in the project's environment, or the answer says they did not.
