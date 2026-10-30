# Development log

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
