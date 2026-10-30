# ml-ai-dev-kit

Plugin for AI and ML development. Version 0.1.0. Author: G0rg0ne.

It can carry skills, hooks, instructions, and rules. A harness loads the pieces it understands. That includes Claude Code, Cursor, GitHub Copilot, and other hosts.

The plugin contains four skills:

- `hello` checks that a harness loaded the plugin.
- `dev-kickoff` creates the folder structure of a new project. It supports three types: an app with a frontend and a backend, a standalone service, or an ML and data science project with notebooks and scripts.
  - It always asks whether to use Docker or uv only, unless the request already says.
  - It applies a modular layout: `core/` for settings and logging, `services/` for business logic, `schemas/`, `adapters/`, thin entry points, and one `tests/` folder.
  - With Docker, it adds a `Dockerfile` that installs with uv, a `compose.yaml` for each project type, and a `.dockerignore`.
- `python-dev-conventions` applies the coding conventions in an existing project:
  - Logging uses loguru with its own config module, which sets each level's color and the date and time format.
  - Code is formatted with ruff.
  - Every test lives in one top-level `tests/` folder.
  - Commands run in the project's own environment.
- `fastapi-backend` builds backends with FastAPI:
  - Each endpoint is its own file with its own router.
  - Each category, such as `/payment` or `/model`, has a router that includes its endpoints.
  - Pydantic schemas validate every request and response.
  - Every variable comes from `.env` through one `Settings` class. Each change that touches a setting shows the full updated `.env.example`.

## What the plugin can hold

- Skills, in `skills/`. Each skill is a folder with a `SKILL.md`. Hosts that read Agent Skills load these.
- Hooks. Scripts that run when a harness event fires. `make test` runs them with sample stdin JSON, without a harness.
- Instructions. Standing guidance a host reads at session start, such as `CLAUDE.md` and `AGENTS.md`.
- Rules. Host-specific rules, such as Cursor rules, written for the harness that reads them.

## Layout

- `skills/hello/SKILL.md`: the `hello` skill
- `skills/python-dev-conventions/SKILL.md`: the `python-dev-conventions` skill
- `skills/python-dev-conventions/references/loguru-config.md`: the house loguru module, level colors, and time format
- `skills/dev-kickoff/SKILL.md`: the `dev-kickoff` skill
- `skills/dev-kickoff/references/`: `app.md`, `service.md`, and `ml-project.md` hold the tree for each project type, and `docker.md` holds the Docker files
- `skills/fastapi-backend/SKILL.md`: the `fastapi-backend` skill
- `skills/fastapi-backend/references/`:
  - `endpoint-pattern.md` has the code for the schema, service, endpoint, category router, app, and test.
  - `settings.md` has `config.py`, `.env.example`, and the test that fails when they drift apart.
- `evals/<case>/prompt.md` and `evals/<case>/graders/*.md`: eval cases for `claude plugin eval`, named `<skill>-<scenario>`. Run one skill's cases with `--case "<skill>-*"`. Results go to `evals/results/`, which git ignores.
- `.claude-plugin/plugin.json`: manifest for the Claude Code package
- `.claude-plugin/marketplace.json`: Claude Code marketplace named `ml-ai-dev-kit`, with this directory as its source

`make sync` publishes skills, instructions, and rules into the folders other hosts read:

- `.agents/skills`
- `.cursor/skills`
- `.github/skills`
- `CLAUDE.md`
- `AGENTS.md`

## Claude Code

Claude Code on `PATH`. From this directory:

1. Add the marketplace:

```
claude plugin marketplace add .
```

2. Install the plugin:

```
/plugin install ml-ai-dev-kit@ml-ai-dev-kit
```

## Check that a harness loaded the plugin

Ask for a hello from this plugin. The `hello` skill replies with these three lines and stops:

```
hello from ml-ai-dev-kit
skill: hello
status: baseline ok
```

## Maintenance

`make` is a shortcut menu for the people maintaining this repo, and for CI. The targets:

| Target | Command |
| --- | --- |
| `make validate` | `claude plugin validate --strict .` checks `plugin.json`, `marketplace.json`, and the plugin's component files |
| `make sync` | `python scripts/sync/sync-skills.py`, then `python scripts/sync/render-instructions.py` |
| `make evals` | `claude plugin eval . --judge-model $(JUDGE_MODEL) --max-cost-usd $(MAX_COST_USD) --no-publish` |
| `make eval-case CASE=<name or glob>` | `claude plugin eval . --case "$(CASE)"` with the same flags as `make evals`, for example `CASE="fastapi-backend-*"` |
| `make test` | `pytest scripts/hooks/tests` feeds sample stdin JSON to the hook scripts, without a harness |
| `make release` | runs the four targets above, then prints the version bump, changelog, and git tag reminder |

A clean `make validate` prints `Validation passed`.

`make evals` runs every case twice: once with the plugin and once without it as a baseline. It pins the judge model to Sonnet, stops at a $3 cost ceiling, and keeps the report local. Override either value on the command line, for example `make evals JUDGE_MODEL=opus MAX_COST_USD=5`. Changes are logged in `DEVELOPMENT.md`.

## License

MIT. See `LICENSE`.

