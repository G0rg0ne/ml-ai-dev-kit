# Docker environment

Development runs in containers; uv still manages dependencies inside them, so `pyproject.toml` and `uv.lock` stay the single source of truth. The source is bind-mounted for live editing, and the virtual environment lives at `/opt/venv` so the mount does not hide it.

## Dockerfile (all types)

```dockerfile
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY . .
RUN uv sync --frozen
```

Replace `latest` with the uv version used to create `uv.lock` (`uv --version`), so builds stay reproducible. Without a local uv, generate the lock file once in a container: `docker run --rm -v "${PWD}:/app" -w /app ghcr.io/astral-sh/uv:latest uv lock`.

## compose.yaml by type

`service`:

```yaml
services:
  app:
    build: .
    env_file: .env
    volumes:
      - .:/app
    command: uv run <project>
```

`app`:

```yaml
services:
  backend:
    build: .
    env_file: .env
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    command: uv run uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
  frontend:
    build: .
    env_file: .env
    environment:
      BACKEND_URL: http://backend:8000
    volumes:
      - .:/app
    ports:
      - "8501:8501"
    command: uv run streamlit run frontend/app.py --server.address 0.0.0.0
    depends_on:
      - backend
```

`ml`:

```yaml
services:
  app:
    build: .
    env_file: .env
    volumes:
      - .:/app
  notebook:
    build: .
    env_file: .env
    volumes:
      - .:/app
    ports:
      - "127.0.0.1:8888:8888"
    command: uv run jupyter lab --ip 0.0.0.0 --no-browser --allow-root
```

Jupyter keeps its token; `docker compose logs notebook` prints the URL with it. The port binds to localhost only.

## .dockerignore

```
.venv/
.git/
**/__pycache__/
.ruff_cache/
.pytest_cache/
.env
```

For `ml`, also `data/` and `models/`: they reach the container through the bind mount, not the image.

## Commands

Every command runs in a container: `docker compose run --rm <service> <command>`, with `app` as the service for `service` and `ml`, and `backend` for `app`.

```
cp .env.example .env
docker compose build
docker compose up
docker compose run --rm app uv run pytest
docker compose run --rm app uv run ruff format
```
