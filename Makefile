.PHONY: validate sync evals eval-case test release

JUDGE_MODEL ?= sonnet
MAX_COST_USD ?= 3

validate:        ## check plugin.json, marketplace.json, skills, agents, hooks, and that AGENTS.md is up to date
	claude plugin validate --strict .
	python3 scripts/sync/render-instructions.py --check

sync:            ## regenerate AGENTS.md from .claude/CLAUDE.md
	python3 scripts/sync/render-instructions.py

evals:           ## run the eval suite against the skills, with and without the plugin
	claude plugin eval . --judge-model $(JUDGE_MODEL) --max-cost-usd $(MAX_COST_USD) --no-publish

eval-case:       ## run one eval case (or a glob), e.g. make eval-case CASE=fastapi-backend-new-endpoint
	@test -n "$(CASE)" || { echo "usage: make eval-case CASE=<case name or glob>"; exit 1; }
	claude plugin eval . --case "$(CASE)" --judge-model $(JUDGE_MODEL) --max-cost-usd $(MAX_COST_USD) --no-publish

test:            ## unit-test the hook and sync scripts without Claude
	python3 -m unittest discover -s scripts/hooks/tests -v
	python3 -m unittest discover -s scripts/sync/tests -v

release: sync validate test evals
	@echo "Next: move [Unreleased] in CHANGELOG.md to the new version, bump version in .claude-plugin/plugin.json, commit, run 'claude plugin tag .', then push with tags."
