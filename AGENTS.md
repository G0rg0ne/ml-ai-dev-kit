<!-- Generated from .claude/CLAUDE.md by `make sync`. Edit .claude/CLAUDE.md, not this file. -->

# ml-ai-dev-kit: instructions for agents

## Structure and purpose

`ml-ai-dev-kit` is a general-purpose kit for coding agents (Claude Code, Cursor, GitHub Copilot, Codex, and other hosts) that packages one developer's way of building Python, AI, and ML projects: how a project starts (Docker or uv, modular layout), how code is written (loguru, ruff, one `tests/` folder), how backends are built (FastAPI, one router per endpoint, Pydantic, settings from `.env`), and how secrets stay out of the agent's reach. It exists so every agent session applies those choices without the person repeating them, and so each choice is measured by evals instead of assumed.

Skills are the portable core, in the open Agent Skills format. The Claude Code plugin (`.claude-plugin/`, `hooks/hooks.json`, `agents/`) is one delivery channel; other hosts receive the skills by copy into their skills folder.

This file guides agents that work **on the kit itself**. The kit's components guide agents that work on **other projects**: keep the two apart.

## Directory layout

| Path | Role |
| --- | --- |
| `.claude-plugin/plugin.json` | Plugin manifest; its `version` is the release version |
| `.claude-plugin/marketplace.json` | Marketplace `ml-ai-dev-kit` that lists this plugin |
| `skills/<name>/SKILL.md` | One skill per folder; detail in `skills/<name>/references/` |
| `agents/<name>.md` | Subagents (currently `security-reviewer`) |
| `hooks/hooks.json` | Hook registration; scripts live in `scripts/hooks/` |
| `scripts/hooks/` | Hook scripts and their tests in `scripts/hooks/tests/` |
| `scripts/sync/` | Generators (`render-instructions.py` writes `AGENTS.md`) and their tests |
| `evals/<skill>-<scenario>/` | Eval cases: `prompt.md` and `graders/*.md`; `evals/results/` is git-ignored |
| `README.md` | Human documentation: install, update, contents, maintenance |
| `.claude/CLAUDE.md` | This file, the source of the agent instructions; kept out of the plugin root so it is not mistaken for plugin content |
| `AGENTS.md` | Generated copy of this file for other hosts; never edit by hand |
| `CHANGELOG.md` | User-facing history, one section per released version |
| `DEVELOPMENT.md` | Detailed development log, one entry per task |
| `Makefile` | `validate`, `sync`, `test`, `evals`, `eval-case`, `release` |

## Conventions

**Host neutrality**
- Skills, references, and agent prompts stay host-neutral: no host-only tool names, slash commands, or paths in their instructions, so the same text works on every host.
- Host-specific wiring (plugin manifests, hook registration, agent frontmatter, future Cursor or Copilot files) lives in that host's packaging, never inside a skill.
- Hook logic stays in scripts that read the tool call as JSON, so another host can reuse it with its own registration.

**Skills**
- Name: kebab-case noun phrase, at most 64 characters, identical to the folder, without "claude" or "anthropic" (`fastapi-backend`, `dev-kickoff`).
- Frontmatter: only `name`, `description`, and `metadata` (`author`, `version`, `date`, all strings), so the skill loads on every Agent Skills host.
- Description: what the skill does, then "Use as soon as..." with the triggers and implicit cases, then "Do not use for... (neighbor skill)". It decides when the skill loads, so it never describes steps.
- Body: only what a model would get wrong without it (house choices, decisions with their default, pitfalls). Long code and tables go to `references/`, linked from the body with when to read them, one level deep.
- One rule lives in one skill. Another skill refers to it by name ("load the `python-dev-conventions` skill") instead of copying it.

**Evals**
- One folder per case, named `<skill>-<scenario>`; the prompt is written as a user would type it and never names the skill.
- One `llm` grader per rule, so a failure names the broken rule, plus a `skill-loaded` grader (`type: tool_used`, `tool: Skill`) as indicator.

**Hooks**
- Python 3.10+ standard library only; read the event as JSON on stdin; exit 2 with the reason on stderr to block, 0 to allow; block when the input cannot be read.
- Registered in `hooks/hooks.json` with `${CLAUDE_PLUGIN_ROOT}` paths and a timeout.

**Agents**
- `agents/<name>.md` with `name`, `description` (what and when), and the smallest `tools` list that does the job.

**Code and text**
- Python: type hints, docstrings, ruff style, tests with the standard `unittest` module (pytest collects them too).
- Documentation in English, plain complete sentences, file and command names in backticks.

## Practices

**Add or change a skill**
1. Check that no existing skill already covers the need; extend it if it does.
2. Write `skills/<name>/SKILL.md` and any `references/`; set `metadata.version` (`0.1.0` for a new skill, bumped on each change) and `metadata.date`.
3. Add at least one eval case `evals/<name>-<scenario>/`; for a rule that the model breaks without the skill, a case that shows it.
4. Run `make validate`, then `make eval-case CASE="<name>-*"`, and read the failed graders before changing anything.
5. If the skill changes how another skill behaves, update the referring skill in the same change.

**Add or change a hook**
1. Write the script in `scripts/hooks/`, register it in `hooks/hooks.json`.
2. Add tests in `scripts/hooks/tests/` for what must be blocked and what must stay allowed; a security hook needs both.
3. Run `make test` and `make validate`.

**Add or change an agent**
1. Write `agents/<name>.md`; state what it never does (for example, modify files) when that matters.
2. Run `make validate`, then try it once on this repository and note the result in `DEVELOPMENT.md`.

**After every change**
- Update `README.md` when contents, commands, or install steps change.
- Add an entry to `DEVELOPMENT.md` and a line under `## [Unreleased]` in `CHANGELOG.md`.
- Edit `.claude/CLAUDE.md`, never `AGENTS.md`, then run `make sync`.

## Testing and validation

| Command | Checks | Cost |
| --- | --- | --- |
| `make validate` | Manifests, skills, agents, hooks (`claude plugin validate --strict`), and that `AGENTS.md` matches `.claude/CLAUDE.md` | Free |
| `make test` | Hook and generator scripts against sample inputs | Free |
| `make eval-case CASE=<name or glob>` | Selected eval cases, with and without the plugin, 3 runs each | About $1 to $2 per case (6 runs) |
| `make evals` | Every eval case; stops at `MAX_COST_USD` (default $3, raise it for the full suite) | Several dollars |

An eval result counts only if the skill loaded (`skill-loaded` passed) and the "with" arm beats the "without" arm. Before a release, every case passes in the "with" arm.

## Guidelines

Do:
- Keep skills short and specific; measure before adding a rule.
- Ask before running a paid eval suite larger than one skill's cases.
- Use placeholders (`change-me`, `<project>`) in every example, template, and eval.

Do not:
- Read, create, edit, or delete `.env` or other secret files, or try to work around the `protect_secrets` hook.
- Put real secrets, usernames, emails, or personal paths in skills, evals, or docs.
- Commit `evals/results/`, caches, or generated files other than `AGENTS.md`.
- Edit `AGENTS.md` by hand, or change behavior without updating `CHANGELOG.md`.
- Rename or remove a skill, agent, or hook outside a release that announces it as breaking.

## Versioning

The plugin follows semantic versioning through `version` in `.claude-plugin/plugin.json`; each skill also carries its own `metadata.version`. While the kit is `0.x`, a minor bump (`0.3.0`) marks new components or changed rules and a patch bump (`0.2.1`) marks fixes. Release steps and the reasoning are in `README.md`, section *Versioning and releases*.
