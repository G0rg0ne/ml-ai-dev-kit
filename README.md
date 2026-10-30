# ml-ai-dev-kit

General-purpose kit for Python, AI, and ML development with coding agents. Version 0.2.0 (see `CHANGELOG.md`). Author: G0rg0ne. License: MIT.

It carries skills, hooks, agents, and instructions. Each host (Claude Code, Cursor, GitHub Copilot, Codex, and others) loads the pieces it understands. The skills use the open Agent Skills format (`SKILL.md`), so they are not tied to one host; the Claude Code plugin package is one of the delivery channels.

## Purpose

The kit packages one way of building projects so that every agent session applies it without being told again:

- **Start** a project the same way: Docker or uv, a modular layout, docs and tests from day one.
- **Write** code the same way: loguru logging, ruff formatting, one `tests/` folder.
- **Build** backends the same way: FastAPI, one router per endpoint, Pydantic validation, settings from `.env`.
- **Protect** secrets: the agent cannot read or change `.env` files, and a reviewer checks the repository for leaks.

Each skill is measured with evals against a baseline without the kit, so a rule stays only if it changes what the agent does.

## Contents

| Component | Kind | What it does |
| --- | --- | --- |
| `dev-kickoff` | Skill | Creates a new app (frontend and backend), service, or ML project. Asks Docker or uv first, then applies the modular layout and the Docker files for the type. |
| `python-dev-conventions` | Skill | loguru with its own config module (level colors, date and time format), ruff formatting, one `tests/` folder, commands in the project's environment. |
| `fastapi-backend` | Skill | One file and router per endpoint, a router per category (`/payment`, `/model`), Pydantic schemas, every variable in `.env`, full `.env.example` shown on each settings change. |
| `hello` | Skill | Replies with three fixed lines, to check that a host loaded the kit. |
| `protect_secrets` | Hook (`PreToolUse`) | Blocks reading, editing, creating, moving, deleting, or grepping `.env` and other secret files, and dumping the environment. `.env.example` stays editable. Needs `python3` on the `PATH`. |
| `security-reviewer` | Subagent | Read-only review of secrets, personal data, leaky artifacts, and git history, with a redacted report by severity. Ask for a security review or use `@security-reviewer`. |

## Host support

| Component | Format | Claude Code | Cursor, GitHub Copilot, Codex, other hosts |
| --- | --- | --- | --- |
| Skills | Agent Skills (`SKILL.md`, portable frontmatter only) | Yes, through the plugin | Yes: copy the skill folders into the host's skills folder (below) |
| `protect_secrets` hook | Python script reading the tool call as JSON; registered in `hooks/hooks.json` | Yes, through the plugin | Not wired yet: each host has its own hook events and registration file |
| `security-reviewer` agent | `agents/security-reviewer.md` | Yes, as a subagent | Not wired yet; on any host, ask the agent to follow that file as instructions |
| Evals | `claude plugin eval` | Yes | Measured on Claude Code only |

## Install

### Claude Code

Requires `python3` on the `PATH` for the hook. From a clone of this repository:

```
claude plugin marketplace add .
claude plugin install ml-ai-dev-kit@ml-ai-dev-kit
```

Once the repository is published on a git host, users add it by its address instead of a local path, for example `claude plugin marketplace add <owner>/ml-ai-dev-kit` for GitHub, or the repository's git URL.

### Other hosts

Copy the folders under `skills/` into the skills folder your host reads, in your project or in your user folder:

| Host | Project skills folder |
| --- | --- |
| Cursor | `.cursor/skills/` |
| GitHub Copilot | `.github/skills/` |
| Codex and hosts following the `.agents` convention | `.agents/skills/` |

Check your host's documentation for the exact folder and for user-level skills. A `make sync` step that publishes the skills to these folders automatically is planned; until then the copy is manual.

### Check the installation

On any host, ask for a hello from this kit. The reply is:

```
hello from ml-ai-dev-kit
skill: hello
status: baseline ok
```

## Get the latest version

`CHANGELOG.md` lists what changed in each version, and what to do for a breaking change.

**Claude Code:**

```
claude plugin marketplace update ml-ai-dev-kit
claude plugin update ml-ai-dev-kit@ml-ai-dev-kit
```

The first command refreshes the marketplace from its source, the second installs the newest version it lists; restart Claude Code to apply it. Claude Code compares the `version` in `plugin.json`, so a change is only delivered once that version is bumped.

**Other hosts:** pull the repository at the latest release tag (`git fetch --tags`, then `git checkout ml-ai-dev-kit--vX.Y.Z`) and copy the skill folders again, replacing the old ones.

## Directory layout

```
ml-ai-dev-kit/
├── .claude-plugin/
│   ├── plugin.json          # Manifest; "version" is the release version
│   └── marketplace.json     # Marketplace "ml-ai-dev-kit" listing this plugin
├── skills/
│   ├── dev-kickoff/         # SKILL.md + references/ (app, service, ml-project, docker)
│   ├── python-dev-conventions/  # SKILL.md + references/loguru-config.md
│   ├── fastapi-backend/     # SKILL.md + references/ (endpoint-pattern, settings)
│   └── hello/               # Baseline skill
├── agents/
│   └── security-reviewer.md # Read-only security review subagent
├── hooks/
│   └── hooks.json           # Registers protect_secrets on PreToolUse
├── scripts/
│   ├── hooks/               # protect_secrets.py + tests/
│   └── sync/                # render-instructions.py (writes AGENTS.md) + tests/
├── evals/
│   ├── <skill>-<scenario>/  # prompt.md + graders/*.md
│   └── results/             # Eval outputs, git-ignored
├── .claude/
│   └── CLAUDE.md            # Instructions for agents working on the kit
├── Makefile                 # validate, sync, test, evals, eval-case, release
├── README.md                # This file
├── AGENTS.md                # Copy of CLAUDE.md in AGENTS.md format (generated)
├── CHANGELOG.md             # Version history
├── DEVELOPMENT.md           # Detailed development log
└── LICENSE
```

## Contributing

Conventions (naming, skill structure, eval and hook rules), the steps to add a skill, hook, or agent, and what is and is not allowed are in `.claude/CLAUDE.md`. Claude Code reads it at session start in this repository; `AGENTS.md` at the root is the same content for hosts that read that file. Edit `.claude/CLAUDE.md` only, then run `make sync`.

`CLAUDE.md` sits in `.claude/` rather than at the root because `claude plugin validate --strict` rejects a root `CLAUDE.md`: plugin users never receive it, and the validator flags it as context that would not ship.

## Testing and validation

| Target | Command | What it checks |
| --- | --- | --- |
| `make validate` | `claude plugin validate --strict .`, then `render-instructions.py --check` | Manifests, skills, agents, hooks; `AGENTS.md` up to date. A clean run prints `Validation passed` and `AGENTS.md is up to date.` |
| `make test` | `python3 -m unittest discover` on `scripts/hooks/tests` and `scripts/sync/tests` | Hook and generator scripts against sample inputs, without Claude |
| `make eval-case CASE=<name or glob>` | `claude plugin eval . --case "$(CASE)"` | Selected cases, for example `CASE="fastapi-backend-*"` |
| `make evals` | `claude plugin eval . --judge-model $(JUDGE_MODEL) --max-cost-usd $(MAX_COST_USD) --no-publish` | Every case, with and without the plugin |
| `make sync` | `python3 scripts/sync/render-instructions.py` | Regenerates `AGENTS.md` from `.claude/CLAUDE.md` |
| `make release` | `sync`, `validate`, `test`, `evals`, then the release reminder | Everything, before a version bump |

Each eval case runs 3 times with the plugin and 3 times without it, so one case costs about $1 to $2 and the full suite more than the default $3 ceiling: raise it with `make evals MAX_COST_USD=7`, or run one skill with `make eval-case`. The judge model defaults to Sonnet (`JUDGE_MODEL`).

## Versioning and releases

The plugin version in `.claude-plugin/plugin.json` follows [Semantic Versioning](https://semver.org/); it is the only version users see. Each skill also has a `metadata.version` that tracks its own changes.

What each bump means:

| Bump | When | Examples |
| --- | --- | --- |
| Major (`2.0.0`) | A user must change something | Renaming or removing a skill, agent, or hook; a hook that blocks more than before; a different generated project layout |
| Minor (`1.3.0`) | New capability, compatible | A new skill, agent, hook, eval case, or rule |
| Patch (`1.3.1`) | Fix without new behavior | Wording, a hook false positive, a broken example |

Suggested path:

- **0.x, now**: the conventions are still moving. Each new component or changed rule is a minor bump, fixes are patches, and a breaking change is a minor bump flagged as breaking in `CHANGELOG.md`. Release the current work as `0.2.0`, then for example the frontend skill as `0.3.0`.
- **1.0.0**: once the conventions held on two or three real projects, every skill has nominal, edge, and negative eval cases, and the hook has been checked in a live session on each host that runs it. From then on, strict semantic versioning.
- **Later**: if some users want changes early, add a second marketplace entry (for example `ml-ai-dev-kit-next`) that points to a development branch, and keep the main entry on tagged releases.

Release steps:

1. Run `make release` (validation, tests, and evals must pass).
2. In `CHANGELOG.md`, rename `## [Unreleased]` to `## [x.y.z] - YYYY-MM-DD` and open a new empty `## [Unreleased]`.
3. Set `version` in `.claude-plugin/plugin.json` to `x.y.z`, and update the version line at the top of this file.
4. Commit, then run `claude plugin tag .` to create the tag `ml-ai-dev-kit--vx.y.z` (it checks that `plugin.json` and the marketplace entry agree).
5. Push the commit and the tag. Users then get it with the two commands in *Get the latest version*.

## License

MIT. See `LICENSE`.
