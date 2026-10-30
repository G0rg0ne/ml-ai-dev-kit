---
type: llm
weight: 1
---

PASS only if the final answer meets every point below. FAIL if any point is missing.

1. The logging uses loguru, not the standard `logging` module as the main logger and not `print`.
2. The loguru configuration sits in its own dedicated module (for example `logging_config.py` inside the package) that exposes a setup function, called once from the entry point, while other modules only import `logger` from loguru.
3. That configuration sets an explicit color for each log level (at least DEBUG, INFO, WARNING, ERROR, CRITICAL), for example through `logger.level("INFO", color=...)`, rather than relying on loguru's default colors.
4. That configuration sets an explicit date and time format in the log format string (for example `{time:YYYY-MM-DD HH:mm:ss.SSS}`).
5. The first test is placed under a top-level `tests/` folder (for example `tests/test_parser.py`), not next to the source code.
6. The answer does not ask whether to use Docker or uv, since the request already says uv.
