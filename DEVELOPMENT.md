# Development log

## [2026-10-30 16:21] - CONFIG

### Changes
- Added `make eval-case CASE=<name or glob>`. It runs only the matching eval cases, with the same judge, cost ceiling, and no-publish flags as `make evals`. It stops with a usage message when `CASE` is empty.

### Files Modified
- `Makefile`, `README.md`

### Rationale
The full suite is 4 cases × 3 runs × 2 arms, or 24 runs, and costs more than the default $3 ceiling. Running one case or one skill keeps iterations cheap.

### Breaking Changes
None

## [2026-10-30 15:50] - FEATURE

### Changes
- Added the `dev-kickoff` skill. It creates the skeleton of three project types: an app with a frontend and a backend, a service, or an ML project. It asks whether to use Docker or uv unless the request says, and creates nothing before the answer. It applies a modular layout. With Docker, it adds a Dockerfile, a compose file for each type, and a `.dockerignore`.
- Added the `fastapi-backend` skill. Each endpoint is its own file with its own `APIRouter`. Each category is a package with a prefixed router, and `api/v1/router.py` includes every category. Pydantic validates requests (`extra="forbid"` and field constraints) and responses (`response_model`). One pydantic-settings `Settings` class reads `.env`. Every change to a setting shows the full `.env.example`. A drift test keeps `Settings` and `.env.example` aligned.
- `python-dev-conventions` 0.2.0: the Docker-or-uv question and the layout moved to `dev-kickoff`. The skill now runs commands in the project's existing environment. The logging module lives in `core/logging_config.py`, or in `shared/logging_config.py` in an app.
- The `dev-kickoff` app tree now uses a `health` category (`/api/v1/health/get_status`), and HTTP services load `fastapi-backend`.
- Eval cases are named `<skill>-<scenario>`. `uv-logging-setup` became `python-dev-conventions-uv-logging`. Added `dev-kickoff-asks-environment`, `dev-kickoff-service-structure`, and `fastapi-backend-new-endpoint`. The structure and backend cases use one LLM grader per rule, so a failure points to the rule it broke.

### Files Modified
- `skills/dev-kickoff/SKILL.md`, `skills/dev-kickoff/references/{app,service,ml-project,docker}.md`
- `skills/fastapi-backend/SKILL.md`, `skills/fastapi-backend/references/{endpoint-pattern,settings}.md`
- `skills/python-dev-conventions/SKILL.md`, `skills/python-dev-conventions/references/loguru-config.md`
- `evals/python-dev-conventions-uv-logging/` (renamed), `evals/dev-kickoff-asks-environment/`, `evals/dev-kickoff-service-structure/`, `evals/fastapi-backend-new-endpoint/`
- `README.md`, `DEVELOPMENT.md`

### Rationale
Project creation, coding conventions, and backend rules are requested separately, so each one is its own skill and the skills load each other. Project types are variants of a single skill, with one reference file per type.

The structure case first used a single grader with six criteria. It passed only 1 of 3 runs even though the answers met every criterion, and the judge's reason for failing them wasn't recorded. After the split into one grader per criterion, it passed 3 of 3.

Eval results (Claude Code 2.1.310, default model, Sonnet as judge, 3 runs per arm):

| Case | With plugin | Without plugin |
| --- | --- | --- |
| `dev-kickoff-asks-environment` | 3/3 | 0/3 |
| `dev-kickoff-service-structure` | 3/3 | 0/3 (22% of points) |
| `fastapi-backend-new-endpoint` | 3/3 | 0/3 (58% of points, never one router per endpoint) |

Total cost for the session: about $5.40.

### Breaking Changes
- `python-dev-conventions` no longer creates projects or asks whether to use Docker or uv. Use `dev-kickoff` for that.
- The eval case `uv-logging-setup` was renamed `python-dev-conventions-uv-logging`.

### Next Steps
- Re-run `dev-kickoff-service-structure` now that HTTP services load `fastapi-backend`.
- Add cases for an app kickoff, an ML kickoff with Docker, and a `fastapi-backend` change to an existing setting.
- Add the frontend skill.
- Run a generated skeleton once with real uv and Docker. This machine has neither, nor Python.

## [2026-10-30 14:41] - CONFIG

### Changes
- `make evals` now pins the judge model, sets a cost ceiling, and skips publishing the report. The judge defaults to Sonnet and the ceiling to $3. Both can be overridden with `JUDGE_MODEL` and `MAX_COST_USD`.

### Files Modified
- `Makefile`, `README.md`

### Rationale
Without `--judge-model`, the judge defaults to Haiku, which is weaker than the model being tested. Without a ceiling, a long suite has no spending limit. These flags make the target safe to run unattended or in CI.

### Breaking Changes
None

## [2026-10-30 13:47] - FEATURE

### Changes
- Added the `python-dev-conventions` skill. It asks whether to use Docker or uv before creating an environment, uses loguru with a dedicated `logging_config.py`, formats with ruff, and keeps every test in a top-level `tests/` folder.
- Added `references/loguru-config.md`, with the level colors, the `YYYY-MM-DD HH:mm:ss.SSS` time format, and the full setup module.
- Added the first eval case, `evals/uv-logging-setup`. It has an `llm` grader for the conventions and a `tool_used: Skill` indicator that shows whether the skill loaded.
- Added `.gitignore`, which excludes `evals/results/`.

### Files Modified
- `skills/python-dev-conventions/SKILL.md`
- `skills/python-dev-conventions/references/loguru-config.md`
- `evals/uv-logging-setup/prompt.md`
- `evals/uv-logging-setup/graders/conventions.md`
- `evals/uv-logging-setup/graders/skill-loaded.md`
- `README.md`, `.gitignore`, `DEVELOPMENT.md`

### Rationale
These conventions are personal preferences that a model does not apply by itself. Without the skill, the baseline used the standard `logging` module. The ask-first rule for Docker or uv is in the skill body. The eval case states uv in its request, so it checks that the skill does not ask when the choice is already given.

Eval run with Claude Code 2.1.310, default model, Sonnet as judge, 3 runs per arm. With the plugin: 3 of 3 passed, and the skill loaded on every run. Without the plugin: 0 of 3. Cost: $0.81.

### Breaking Changes
None

### Next Steps
- Add cases where the environment is not stated, so the agent must ask whether to use Docker or uv. Add a Docker case and a negative case for a non-Python project.
- Run the loguru module once under Python 3.12. It was not executed here because this machine has no Python interpreter.
