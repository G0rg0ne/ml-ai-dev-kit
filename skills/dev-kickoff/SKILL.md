---
name: dev-kickoff
description: >
  Creates the folder structure and starter files of a new Python project:
  a full app with frontend and backend, a standalone backend service, or
  an ML and data science project with notebooks and scripts. Use as soon
  as someone starts, kicks off, bootstraps, or scaffolds a new project or
  repository, even without the word structure. Do not use for adding code
  to an existing project (python-dev-conventions).
metadata:
  author: "G0rg0ne"
  version: "0.1.0"
  date: "2026-10-30"
---

# Dev kickoff

Creates the skeleton of a new project: folders, configuration, environment, and minimal entry points that run. Features come later, from the person or from the frontend and backend skills; this skill does not write business code.

## Inputs

| Input | Values | How to get it |
| --- | --- | --- |
| Project type | `app` (frontend and backend), `service` (backend, API, worker, or CLI alone), `ml` (notebooks, training, datasets, analysis) | Deduce from the request; ask if two types fit |
| Project name | kebab-case for the folder (`payments-api`), snake_case for the Python package (`payments_api`) | Ask if missing |
| Environment | `docker` or `uv` | Always ask, unless the request states it, because the author decides per project. List Docker first, as the author's usual choice |

Ask every missing input in one message, restate the deduced ones so the person can correct them, then stop and wait for the answer. Create nothing before the environment is known: picking one silently is the failure this skill exists to prevent. If the target folder already holds a project, stop and say so instead of overwriting it.

## Create the project

1. Read the reference for the type and create exactly its tree and files: `references/app.md`, `references/service.md`, or `references/ml-project.md`. Empty folders get a `.gitkeep`.
2. If the environment is `docker`, also read `references/docker.md` and add the files it gives for that type.
3. Load the `python-dev-conventions` skill and apply it to the skeleton: the loguru config module, the ruff and pytest configuration in `pyproject.toml`, and the `tests/` folder. For an `app`, or a `service` that exposes HTTP, also load `fastapi-backend` for the backend files.
4. Write the files every type shares:
   - `README.md`: purpose, structure, setup and run commands for the chosen environment, how to run tests, environment variables.
   - `DEVELOPMENT.md`: a first entry dated now, type Feature, listing the skeleton created.
   - `.env.example`: every variable read by `core/config.py`, with a safe default or a placeholder.
   - `.gitignore`: Python caches, `.venv/`, `.env`, plus the type's additions.
5. Install and check, with the commands of the chosen environment: lock the dependencies, format, then run the tests (the skeleton ships one passing test). If `uv` or `docker` is not installed, skip the step and say which commands remain to run.
6. End with the created tree, the commands to run the project, and what was not verified.

## Modular structure

These rules hold for every type and explain the references' trees:

- **One responsibility per folder.** Settings and logging in `core/`, business logic in `services/` (or domain folders in `ml`), data shapes in `schemas/`, access to external systems (databases, HTTP clients, storage) in `adapters/` or `db/`.
- **Thin entry points.** `main.py`, `scripts/*.py`, and notebooks parse inputs, call `setup_logging()`, and delegate to the package. Logic that a notebook or script needs twice moves into the package.
- **Settings from the environment.** `core/config.py` reads them with pydantic-settings; nothing secret is hard-coded.
- **One `tests/` folder at the root**, mirroring the source tree.
- **Python 3.12**, dependencies declared in `pyproject.toml` and locked in `uv.lock` in both environments.
