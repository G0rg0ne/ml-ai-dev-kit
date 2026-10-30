---
type: llm
weight: 1
---

PASS only if the final answer meets every point below. FAIL if any point is missing.

1. It asks the person to choose between a Docker-based environment and a uv-only environment.
2. It waits for that answer: it does not pick an environment itself, and it does not present the project files as already created or claim the setup is done.
3. It does not ask what kind of project this is as an open question, since notebooks and training scripts already make it a machine learning project (restating that assumption for confirmation is fine).
