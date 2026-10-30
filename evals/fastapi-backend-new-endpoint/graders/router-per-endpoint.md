---
type: llm
weight: 1
---

PASS if the answer uses FastAPI and puts the endpoint in its own file inside a category folder (for example `api/v1/endpoints/model/get_available_models.py`) that defines its own `APIRouter`, and a separate category router (for example in that folder's `__init__.py`) with a category prefix such as `/model` that includes the endpoint router, itself included in an API-level router or app. FAIL if the endpoint is defined directly on the app, or several endpoints or categories share one file without a category router.
