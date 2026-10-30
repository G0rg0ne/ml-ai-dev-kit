---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

My backend is a Python API package called `shop_api` (src layout). I need a first endpoint that returns the list of models available for recommendations, filtered by task (for example "ranking" or "similarity") with a maximum number of results. The model registry it calls lives at a URL that changes between environments and needs an API token. Show me every file I need to add or change, with the code; don't create the files.
