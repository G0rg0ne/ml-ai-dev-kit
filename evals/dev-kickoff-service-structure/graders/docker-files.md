---
type: llm
weight: 1
---

PASS if the answer shows the content of three files: a `Dockerfile` that installs dependencies with uv (for example `uv sync`) using `pyproject.toml` and `uv.lock`; a `compose.yaml` with a volume mounting the project source into the container; and a `.dockerignore`. FAIL if any of the three is missing or if the Dockerfile installs dependencies with pip instead of uv.
