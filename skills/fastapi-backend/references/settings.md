# Settings and .env

## `<root>/core/config.py`

```python
"""Application settings, read from the environment and .env."""

from functools import lru_cache
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Every configurable value of the backend."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Application
    app_name: str = "<project>"
    app_version: str = "0.1.0"
    environment: Literal["local", "staging", "production"] = "local"
    log_level: str = "INFO"

    # API
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:8501"]

    # Payment provider
    payment_provider_api_key: SecretStr
    payment_provider_timeout_seconds: float = 10.0


@lru_cache
def get_settings() -> Settings:
    """Return the settings, loaded once."""
    return Settings()
```

Field names map to upper-case variables (`payment_provider_api_key` reads `PAYMENT_PROVIDER_API_KEY`). List and dict fields are written as JSON in `.env`.

## `.env.example`

Same groups and order as `Settings`; one line per field; secrets get a placeholder, never a real value.

```dotenv
# Application
APP_NAME=<project>
APP_VERSION=0.1.0
ENVIRONMENT=local
LOG_LEVEL=INFO

# API
API_V1_PREFIX=/api/v1
CORS_ORIGINS=["http://localhost:8501"]

# Payment provider
PAYMENT_PROVIDER_API_KEY=change-me
PAYMENT_PROVIDER_TIMEOUT_SECONDS=10.0
```

The person copies it once with `cp .env.example .env` and fills in the secrets. After a change, tell them which keys to add to their existing `.env`.

## Drift test: `tests/core/test_env_example.py`

```python
"""Keep .env.example in sync with Settings."""

from pathlib import Path

from <root>.core.config import Settings

ENV_EXAMPLE = Path(__file__).resolve().parents[2] / ".env.example"


def test_env_example_lists_every_setting() -> None:
    lines = ENV_EXAMPLE.read_text(encoding="utf-8").splitlines()
    keys = {
        line.split("=", 1)[0].strip()
        for line in lines
        if line.strip() and not line.lstrip().startswith("#")
    }
    assert keys == {name.upper() for name in Settings.model_fields}
```

## `tests/conftest.py`

Required secrets have no default, so tests provide fake values before any app import:

```python
import os

os.environ.setdefault("PAYMENT_PROVIDER_API_KEY", "test-key")
```
