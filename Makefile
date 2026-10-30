.PHONY: validate sync evals test release

validate:        ## check plugin.json, marketplace.json, every SKILL.md
	claude plugin validate --strict .

sync:            ## regenerate .agents/skills, .cursor/skills, .github/skills, CLAUDE.md, AGENTS.md
	python scripts/sync/sync-skills.py
	python scripts/sync/render-instructions.py

evals:           ## run the eval suite against the skills
	claude plugin eval

test:            ## unit-test the hook scripts without Claude (feed them sample stdin JSON)
	pytest scripts/hooks/tests

release: validate sync evals test
	@echo "bump version in .claude-plugin/plugin.json, update CHANGELOG.md, then git tag"
