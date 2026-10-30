# ml-ai-dev-kit

Plugin for AI and ML development. Version 0.1.0. Author: G0rg0ne.

It can carry skills, hooks, instructions, and rules. A harness loads the pieces it understands. That includes Claude Code, Cursor, GitHub Copilot, and other hosts.

The plugin contains two skills:

- `hello` checks that a harness loaded the plugin.
- `python-dev-conventions` sets up and maintains Python projects with the author's conventions:
  - It asks whether to use a Docker or a uv environment before creating one.
  - It uses loguru with its own config module, which sets each level's color and the date and time format.
  - It formats the code with ruff.
  - It keeps every test in one top-level `tests/` folder.

## What the plugin can hold

- Skills, in `skills/`. Each skill is a folder with a `SKILL.md`. Hosts that read Agent Skills load these.
- Hooks. Scripts that run when a harness event fires. `make test` runs them with sample stdin JSON, without a harness.
- Instructions. Standing guidance a host reads at session start, such as `CLAUDE.md` and `AGENTS.md`.
- Rules. Host-specific rules, such as Cursor rules, written for the harness that reads them.

## Layout

- `skills/hello/SKILL.md`: the `hello` skill
- `skills/python-dev-conventions/SKILL.md`: the `python-dev-conventions` skill
- `skills/python-dev-conventions/references/loguru-config.md`: the house loguru module, level colors, and time format
- `evals/<case>/prompt.md` and `evals/<case>/graders/*.md`: eval cases for `claude plugin eval`. Results go to `evals/results/`, which git ignores.
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
| `make test` | `pytest scripts/hooks/tests` feeds sample stdin JSON to the hook scripts, without a harness |
| `make release` | runs the four targets above, then prints the version bump, changelog, and git tag reminder |

A clean `make validate` prints `Validation passed`.

`make evals` runs every case twice: once with the plugin and once without it as a baseline. It pins the judge model to Sonnet, stops at a $3 cost ceiling, and keeps the report local. Override either value on the command line, for example `make evals JUDGE_MODEL=opus MAX_COST_USD=5`. Changes are logged in `DEVELOPMENT.md`.

## License

MIT. See `LICENSE`.

