import uuid
from typing import Any

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.monitor import Monitor
from src.models.user import User


async def create_user_in_db(
    db_session: AsyncSession,
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


async def create_monitor_in_db(
    db_session: AsyncSession,
    user_id: uuid.UUID,
    name: str = "My Monitor",
    url: str = "https://example.com",
    check_interval: int = 60,
    timeout: int = 10,  # noqa: ASYNC109
    expected_status: int = 200,
    is_active: bool = True,
) -> Monitor:
    monitor = Monitor(
        user_id=user_id,
        name=name,
        url=url,
        check_interval=check_interval,
        timeout=timeout,
        expected_status=expected_status,
        is_active=is_active,
    )
    db_session.add(monitor)
    await db_session.commit()
    await db_session.refresh(monitor)
    return monitor


async def get_auth_headers(
    client: AsyncClient,
    email: str = "user@example.com",
    password: str = "secret123",
) -> dict[str, Any]:
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
