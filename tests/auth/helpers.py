from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from httpx import AsyncClient

from src.core.config import settings
from src.models import User


async def register_user(
    client: AsyncClient,
    email: str = "user@example.com",
    password: str = "secret123",  # noqa: S107
) -> dict[str, Any]:
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    assert response.status_code == 201
    return response.json()


async def login_user(
    client: AsyncClient,
    email: str = "user@example.com",
    password: str = "secret123",
) -> dict[str, Any]:
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    assert response.status_code == 200
    return response.json()


async def create_user(
    db_session: Any,
    email: str = "user@example.com",
    password: str = "secret123",
    is_active: bool = True,
) -> User:
    user = User(
        email=email.lower(),
        hashed_password=f"hashed:{password}",
        is_active=is_active,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


def make_token(
    *,
    user_id: str,
    token_type: str,
    expires_delta: timedelta = timedelta(minutes=5),
) -> str:
    payload = {
        "sub": user_id,
        "type": token_type,
        "exp": datetime.now(UTC) + expires_delta,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
