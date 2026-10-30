---
type: llm
weight: 1
---

PASS if the registry URL and API token are read through a pydantic-settings `Settings` class loaded from `.env` (the token as `SecretStr` or otherwise kept secret), injected into the code rather than read with `os.getenv` or hard-coded in the endpoint or service. FAIL if either value is hard-coded or read directly with `os.getenv`/`os.environ` outside the settings class.
