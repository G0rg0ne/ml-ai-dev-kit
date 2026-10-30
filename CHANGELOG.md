# Changelog

All notable changes to `ml-ai-dev-kit`. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/). Detailed development notes are in `DEVELOPMENT.md`.

## [Unreleased]

## [0.2.0] - 2026-10-30

### Added
- `dev-kickoff` skill: creates the skeleton of an app (frontend and backend), a service, or an ML project; asks Docker or uv first; modular layout; Docker files per type.
- `python-dev-conventions` skill: loguru with its own config module (level colors, date and time format), ruff formatting, one `tests/` folder, commands in the project's environment.
- `fastapi-backend` skill: one file and router per endpoint, category routers, Pydantic validation, settings from `.env` with the full `.env.example` shown on every change.
- `protect_secrets` hook: blocks agent access to `.env` and other secret files, and environment dumps.
- `security-reviewer` subagent: read-only review of secrets, personal data, leaky artifacts, and git history.
- Eval cases for the three skills, `make eval-case`, and `make test` for the scripts.
- `.claude/CLAUDE.md` (instructions for agents working on the kit), `AGENTS.md` generated from it, and this changelog.

### Changed
- `make validate` also checks that `AGENTS.md` is up to date; `make sync` generates it.
- Documentation presents the kit as host-neutral, with a host support table and install and update steps for Claude Code and for other hosts.

## [0.1.0] - 2026-10-30

### Added
- Plugin manifest, local marketplace, and the `hello` baseline skill.
