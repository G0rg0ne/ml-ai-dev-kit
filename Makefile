.PHONY: validate sync evals eval-case test release

JUDGE_MODEL ?= sonnet
MAX_COST_USD ?= 3

validate:        ## check plugin.json, marketplace.json, every SKILL.md
	claude plugin validate --strict .

sync:            ## regenerate .agents/skills, .cursor/skills, .github/skills, CLAUDE.md, AGENTS.md
	python scripts/sync/sync-skills.py
	python scripts/sync/render-instructions.py

evals:           ## run the eval suite against the skills, with and without the plugin
	claude plugin eval . --judge-model $(JUDGE_MODEL) --max-cost-usd $(MAX_COST_USD) --no-publish

eval-case:       ## run one eval case (or a glob), e.g. make eval-case CASE=fastapi-backend-new-endpoint
	@test -n "$(CASE)" || { echo "usage: make eval-case CASE=<case name or glob>"; exit 1; }
	claude plugin eval . --case "$(CASE)" --judge-model $(JUDGE_MODEL) --max-cost-usd $(MAX_COST_USD) --no-publish

test:            ## unit-test the hook scripts without Claude (feed them sample stdin JSON)
	pytest scripts/hooks/tests

release: validate sync evals test
	@echo "bump version in .claude-plugin/plugin.json, update CHANGELOG.md, then git tag"
