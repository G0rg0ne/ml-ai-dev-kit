# Development log

## [2026-11-01 19:30] - FEATURE

### Changes
- Added `.cursor-plugin/plugin.json`: name, version, author, license, and keywords, with `skills` set to `./skills/` and `agents` set to `./agents/`. `hooks` is left out on purpose.
- Added `.cursor-plugin/marketplace.json` listing the plugin, for team marketplace import.
- Added `scripts/sync/tests/test_cursor_plugin.py`: the Cursor manifest has the same `name` and `version` as the Claude one, its paths exist inside the repository, every skill folder has a `SKILL.md`, and the marketplace lists the plugin.
- `README.md`: new *Cursor* install section (local folder for Windows and Unix, team marketplace, public marketplace), a Cursor column in the host support table, a Cursor update note, the new folder in the directory layout, and the second manifest in the release steps.
- `.claude/CLAUDE.md` mentions the Cursor files in the layout table, host neutrality, and versioning; regenerated `AGENTS.md` with `make sync`.

### Files Modified
- `.cursor-plugin/plugin.json`, `.cursor-plugin/marketplace.json`, `scripts/sync/tests/test_cursor_plugin.py`, `README.md`, `.claude/CLAUDE.md`, `AGENTS.md`, `CHANGELOG.md`, `DEVELOPMENT.md`

### Rationale
Cursor reads `.cursor-plugin/plugin.json` and the same `SKILL.md` and agent files, so no skill changed (host neutrality holds). The manifest follows Cursor's plugin reference: only `name` is required, `displayName` does not exist, and paths are relative. The hook is not registered: Cursor's event names (`preToolUse`) and tool names differ from the Claude ones that `protect_secrets.py` checks, so wiring it needs script changes and tests of its own. The version now lives in two manifests; the test prevents drift.

### Breaking Changes
None.

### Next Steps
- Install locally in Cursor and check that the three skills and the agent load. The `tools` key in `agents/security-reviewer.md` is Claude Code frontmatter; Cursor's docs do not say whether it ignores unknown keys.
- Decide whether to wire `protect_secrets` for Cursor with a `hooks/hooks-cursor.json` and tool-name handling in the script.
- Check that a single-plugin repository imports as a team marketplace; Cursor's docs only describe `marketplace.json` for multi-plugin repositories.

## [2026-10-30 17:40] - CONFIG

### Changes
- Set the plugin version to `0.2.0` in `.claude-plugin/plugin.json`.
- Renamed `[Unreleased]` in `CHANGELOG.md` to `[0.2.0] - 2026-10-30` and opened a new empty `[Unreleased]` section.
- Updated the version line in `README.md`.

### Files Modified
- `.claude-plugin/plugin.json`, `CHANGELOG.md`, `README.md`, `DEVELOPMENT.md`

### Rationale
Everything since 0.1.0 adds components: three skills, a hook, a subagent, evals, and docs. That makes it a minor bump under the 0.x policy in the README. Claude Code only delivers an update once this version changes.

### Breaking Changes
None for users of 0.1.0, which contained only the `hello` skill.

### Next Steps
- Run the full eval suite with `make evals MAX_COST_USD=7`, commit, tag with `claude plugin tag .`, and push.

## [2026-10-30 17:26] - DOCS

### Changes
- `README.md` describes the kit as general-purpose. The Claude Code plugin is one delivery channel.
- Added a host support table: skills work everywhere, while the hook, subagent, and evals are wired for Claude Code only so far.
- Install and update steps are now split between Claude Code and other hosts. For Cursor (`.cursor/skills/`), GitHub Copilot (`.github/skills/`), and Codex (`.agents/skills/`), the skill folders are copied by hand until `make sync` publishes them.
- `.claude/CLAUDE.md` states the same scope and adds a host-neutrality convention:
  - Skills and agent prompts contain no host-only instructions.
  - Host wiring stays in each host's packaging.
  - Hook logic stays in scripts that can be reused.
- Regenerated `AGENTS.md`.

### Files Modified
- `README.md`, `.claude/CLAUDE.md`, `AGENTS.md`, `CHANGELOG.md`, `DEVELOPMENT.md`

### Rationale
The previous docs called the kit a Claude Code plugin, which contradicted its purpose. The support table states what each host gets today, so users of other hosts know the hook and subagent are not active for them yet.

### Breaking Changes
None

### Next Steps
- Publish the skills to each host's folder with `make sync`.
- Wire `protect_secrets` into Cursor hooks and other hosts' hooks, and port `security-reviewer` to hosts that support subagents.

## [2026-10-30 17:15] - DOCS

### Changes
- Rewrote `README.md`. It covers:
  - Purpose and a contents table.
  - Install and updating to the latest version.
  - The directory tree, testing and validation, and contributing.
  - A versioning policy: semantic versioning, what each bump means, a path from `0.x` to `1.0.0`, an optional `-next` channel, and release steps with `claude plugin tag`.
- Added `.claude/CLAUDE.md`, the instructions for agents working on the kit: structure and purpose, directory layout, conventions, practices for adding skills, hooks, and agents, testing and validation, guidelines, and versioning.
- Added `AGENTS.md`, generated from `.claude/CLAUDE.md` by `scripts/sync/render-instructions.py`. It has a "generated, do not edit" header, and its `--check` mode reports drift.
- Added `CHANGELOG.md` in Keep a Changelog format: everything since 0.1.0 is under `[Unreleased]`, planned as 0.2.0.
- Makefile changes:
  - `make sync` now only generates `AGENTS.md`. It used to call two scripts that didn't exist.
  - `make validate` also runs the drift check.
  - `make test` also runs the sync tests.
  - `make release` prints the full release steps.

### Files Modified
- `README.md`, `.claude/CLAUDE.md`, `AGENTS.md`, `CHANGELOG.md`, `DEVELOPMENT.md`, `Makefile`
- `scripts/sync/render-instructions.py`, `scripts/sync/tests/test_render_instructions.py`

### Rationale
`CLAUDE.md` lives in `.claude/` because `claude plugin validate --strict` fails on a root `CLAUDE.md`: plugin users never receive it. Claude Code still loads `.claude/CLAUDE.md` as project context in this repository.

`AGENTS.md` is generated rather than hand-copied, so the two files can't drift apart silently.

`CHANGELOG.md` is for users, one section per release. `DEVELOPMENT.md` stays the detailed log for maintainers.

### Breaking Changes
- `make sync` no longer claims to publish skills to `.agents/skills`, `.cursor/skills`, or `.github/skills`. That was never implemented.

### Next Steps
- Release 0.2.0 by following the README release steps.
- Publish the repository on a git host so users can add the marketplace by address.
- Implement skill syncing for other hosts if Cursor or Copilot users need it.

## [2026-10-30 16:43] - FEATURE

### Changes
- Added the `protect_secrets` `PreToolUse` hook. It blocks, with exit code 2 and a reason:
  - `Read`, `Edit`, `Write`, `MultiEdit`, and `NotebookEdit` on secret files.
  - `Grep` with a secret path or glob.
  - `Bash` commands that mention a secret file or dump the environment.
- Secret files are `.env`, `.env.*`, and `*.env`; `*.pem`, `*.key`, `*.p12`, `*.pfx`, and keystores; `id_rsa` and other SSH keys; `.netrc`, `.pgpass`, `.pypirc`, and `.npmrc`; `credentials` files; and `secrets.*` files.
- Templates (`.example`, `.sample`, `.template`, `.dist`) are allowed.
- Unreadable hook input blocks the call (fail closed).
- Added the `security-reviewer` subagent. It is read-only, with the Read, Grep, Glob, and Bash tools. It looks for secrets, tracked secret files, personal data, leaky artifacts, and git history leaks. It uses gitleaks or trufflehog when installed, and reports redacted findings by severity with fixes.
- `make test` now runs the hook tests with `unittest`, which pytest can also collect, so they run without third-party packages.

### Files Modified
- `hooks/hooks.json`, `scripts/hooks/protect_secrets.py`, `scripts/hooks/tests/test_protect_secrets.py`
- `agents/security-reviewer.md`
- `Makefile`, `README.md`, `DEVELOPMENT.md`

### Rationale
A skill can't guarantee the agent stays away from `.env`, but a hook runs on every tool call. Blocking by file name, and by file name inside shell commands, covers the usual paths: `cat`, `rm`, `mv`, `cp`, redirection, `source`, and `--env-file`.

`Glob` stays allowed, because it lists names without contents. That lets the reviewer report that a `.env` exists, and whether it is tracked, without reading it.

The reviewer is a subagent, so it scans with its own context and returns a report, not raw search output.

### Breaking Changes
- The agent can no longer create `.env` from `.env.example` (`cp .env.example .env`) or run commands with `--env-file .env`. The person runs those commands.

### Known Limits
- `Grep` over a whole directory isn't blocked, so a broad search can still show lines of an untracked `.env` if ripgrep doesn't skip it. ripgrep skips git-ignored files by default.
- Commands that build a file name indirectly, such as variables or `find -exec`, aren't detected.
- `echo .env >> .gitignore` is blocked as a false positive. Edit `.gitignore` with the Edit tool instead.
- The hook was tested with sample events (12 unittest cases, Python 3.14 in WSL), not yet in a live Claude Code session.

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
