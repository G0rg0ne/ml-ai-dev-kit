# Endpoint pattern

Full code for one category (`payment`) with one endpoint (`get_user`). Replace `<root>` with `backend.app` in an app, or `<package>` in a service.

## Schema: `<root>/schemas/payment.py`

```python
"""Request and response schemas of the payment category."""

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class GetUserRequest(BaseModel):
    """Query parameters of GET /payment/get_user."""

    model_config = ConfigDict(extra="forbid")

    user_id: int = Field(gt=0)
    include_history: bool = False


class PaymentUserResponse(BaseModel):
    """Payment profile of a user."""

    user_id: int
    currency: Literal["EUR", "USD", "GBP"]
    balance: Decimal
```

## Service: `<root>/services/payment.py`

```python
"""Business logic of the payment category."""

from loguru import logger

from <root>.schemas.payment import PaymentUserResponse


class UserNotFoundError(Exception):
    """Raised when the user does not exist."""


class PaymentService:
    """Payment operations, independent of HTTP."""

    def __init__(self, provider_api_key: str, timeout_seconds: float) -> None:
        self._provider_api_key = provider_api_key
        self._timeout_seconds = timeout_seconds

    async def get_user(self, user_id: int) -> PaymentUserResponse:
        """Return the payment profile of a user."""
        logger.debug("Fetching payment user {user_id}", user_id=user_id)
        raise UserNotFoundError(f"User {user_id} not found")
```

## Dependencies: `<root>/api/deps.py`

```python
"""Shared FastAPI dependencies."""

from typing import Annotated

from fastapi import Depends

from <root>.core.config import Settings, get_settings
from <root>.services.payment import PaymentService

SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_payment_service(settings: SettingsDep) -> PaymentService:
    """Build the payment service from settings."""
    return PaymentService(
        provider_api_key=settings.payment_provider_api_key.get_secret_value(),
        timeout_seconds=settings.payment_provider_timeout_seconds,
    )
```

## Endpoint: `<root>/api/v1/endpoints/payment/get_user.py`

```python
"""GET /payment/get_user: payment profile of a user."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from <root>.api.deps import get_payment_service
from <root>.schemas.payment import GetUserRequest, PaymentUserResponse
from <root>.services.payment import PaymentService, UserNotFoundError

router = APIRouter()


@router.get(
    "/get_user",
    response_model=PaymentUserResponse,
    summary="Get the payment profile of a user",
)
async def get_user(
    params: Annotated[GetUserRequest, Query()],
    service: Annotated[PaymentService, Depends(get_payment_service)],
) -> PaymentUserResponse:
    """Return the payment profile of a user."""
    try:
        return await service.get_user(params.user_id)
    except UserNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
```

A POST endpoint takes its body as a parameter typed with its request schema (`payload: CreatePaymentRequest`) and sets `status_code=status.HTTP_201_CREATED` when it creates something.

## Category router: `<root>/api/v1/endpoints/payment/__init__.py`

```python
"""Payment category: every endpoint under /payment."""

from fastapi import APIRouter

from <root>.api.v1.endpoints.payment import get_user

router = APIRouter(prefix="/payment", tags=["payment"])
router.include_router(get_user.router)
```

## API router: `<root>/api/v1/router.py`

```python
"""Version 1 of the API: every category router."""

from fastapi import APIRouter

from <root>.api.v1.endpoints import health, payment

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(payment.router)
```

## Application: `<root>/main.py`

```python
"""FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from <root>.api.v1.router import api_router
from <root>.core.config import get_settings
from <logging module> import setup_logging

settings = get_settings()
setup_logging(settings.log_level)

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix=settings.api_v1_prefix)
```

`<logging module>` is `shared.logging_config` in an app, `<package>.core.logging_config` in a service.

## Test: `tests/api/v1/payment/test_get_user.py`

```python
"""Tests of GET /api/v1/payment/get_user."""

from decimal import Decimal

from fastapi.testclient import TestClient

from <root>.api.deps import get_payment_service
from <root>.main import app
from <root>.schemas.payment import PaymentUserResponse


class FakePaymentService:
    async def get_user(self, user_id: int) -> PaymentUserResponse:
        return PaymentUserResponse(user_id=user_id, currency="EUR", balance=Decimal("10"))


def test_get_user_returns_profile() -> None:
    app.dependency_overrides[get_payment_service] = FakePaymentService
    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/payment/get_user", params={"user_id": 1})
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["user_id"] == 1


def test_get_user_rejects_invalid_id() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/payment/get_user", params={"user_id": 0})
    assert response.status_code == 422
```

`tests/conftest.py` sets the required secrets before the app is imported (see `settings.md`).
