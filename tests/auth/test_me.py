from datetime import timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.auth.helpers import create_user, login_user, make_token


async def test_get_current_user_success(
    client: AsyncClient,
    db_session: AsyncSession,
):
    await create_user(db_session)
    tokens = await login_user(client)

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == "user@example.com"


async def test_get_current_user_without_token_returns_unauthorized(
    client: AsyncClient,
):
    response = await client.get("/api/v1/auth/me")

    assert response.status_code == 401


async def test_get_current_user_rejects_refresh_token(
    client: AsyncClient,
    db_session: AsyncSession,
):
    await create_user(db_session)
    tokens = await login_user(client)

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tokens['refresh_token']}"},
    )

    assert response.status_code == 401
    assert response.json()["code"] == "invalid_token"


@pytest.mark.parametrize(
    "token",
    [
        "not-a-jwt",
        make_token(user_id="not-a-uuid", token_type="access"),
        make_token(
            user_id="00000000-0000-0000-0000-000000000000",
            token_type="access",
        ),
        make_token(
            user_id="00000000-0000-0000-0000-000000000000",
            token_type="access",
            expires_delta=timedelta(seconds=-1),
        ),
    ],
)
async def test_get_current_user_rejects_invalid_tokens(
    client: AsyncClient,
    token: str,
):
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert response.json() == {
        "message": "Could not validate credentials",
        "code": "invalid_token",
    }


async def test_get_current_user_rejects_inactive_user(
    client: AsyncClient,
    db_session: AsyncSession,
):
    inactive_user = await create_user(db_session, is_active=False)
    token = make_token(user_id=str(inactive_user.id), token_type="access")

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert response.json()["code"] == "inactive_user"
