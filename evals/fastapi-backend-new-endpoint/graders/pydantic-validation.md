---
type: llm
weight: 1
---

PASS if the request input (the task filter and the maximum number of results) is validated by Pydantic with explicit constraints (for example a model or `Query` with `Literal` or an enum for the task and `gt`/`le` bounds on the limit), and the route declares a Pydantic response schema (`response_model` or a schema return type) defined in a schemas module. FAIL if the input is unconstrained or the endpoint returns raw dicts without a response schema.
