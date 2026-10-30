---
type: llm
weight: 1
---

PASS if the package separates business logic (for example a `services/` folder) from data shapes (for example `schemas/`) and from access to external systems (for example `adapters/` or `db/`), each in its own folder, and has an entry point module such as `main.py`. FAIL if any of these is missing or if they are merged into one folder.
