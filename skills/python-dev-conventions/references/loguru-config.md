# Loguru configuration

The house logging setup. Copy the module below into `src/<package>/core/logging_config.py` (or `shared/logging_config.py` in an app with a frontend and a backend) and adapt only the package name, unless the person asks for other colors or formats.

## House style

Date and time format: `YYYY-MM-DD HH:mm:ss.SSS` (local time, milliseconds).

| Level | Color tag |
| --- | --- |
| TRACE | `<dim><cyan>` |
| DEBUG | `<blue>` |
| INFO | `<white><bold>` |
| SUCCESS | `<green><bold>` |
| WARNING | `<yellow><bold>` |
| ERROR | `<red><bold>` |
| CRITICAL | `<white><bold><RED>` (white on red background) |

Line format: time in green, level padded to 8 characters in its level color, location in cyan, message in its level color.

## Module

```python
"""Logging configuration for the application, built on loguru."""

import logging
import os
import sys

from loguru import logger

TIME_FORMAT = "YYYY-MM-DD HH:mm:ss.SSS"

LOG_FORMAT = (
    f"<green>{{time:{TIME_FORMAT}}}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

LEVEL_COLORS: dict[str, str] = {
    "TRACE": "<dim><cyan>",
    "DEBUG": "<blue>",
    "INFO": "<white><bold>",
    "SUCCESS": "<green><bold>",
    "WARNING": "<yellow><bold>",
    "ERROR": "<red><bold>",
    "CRITICAL": "<white><bold><RED>",
}


class InterceptHandler(logging.Handler):
    """Forward records from the standard logging module to loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging(level: str | None = None, log_file: str | None = None) -> None:
    """Configure loguru once, at application start.

    Args:
        level: Minimum level; defaults to the LOG_LEVEL env var, then INFO.
        log_file: Optional path of a rotating file sink, written without colors.
    """
    level = (level or os.getenv("LOG_LEVEL", "INFO")).upper()

    logger.remove()
    for name, color in LEVEL_COLORS.items():
        logger.level(name, color=color)

    logger.add(sys.stderr, level=level, format=LOG_FORMAT, colorize=True)
    if log_file:
        logger.add(
            log_file,
            level=level,
            format=LOG_FORMAT,
            colorize=False,
            rotation="10 MB",
            retention="14 days",
            enqueue=True,
        )

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
```

## Usage

```python
# entry point, for example src/<package>/__main__.py
from <package>.core.logging_config import setup_logging

setup_logging()
```

```python
# any other module
from loguru import logger

logger.info("Parsed {count} rows", count=len(rows))
```

`setup_logging()` changes global state, so only the entry point calls it; tests that need to capture logs add their own sink in a fixture in `tests/conftest.py` and remove it afterwards.
