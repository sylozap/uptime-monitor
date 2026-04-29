from datetime import timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.auth.helpers import create_user, login_user, make_token


async def test_refresh_success_returns_new_token_pair(
    client: AsyncClient,
    db_session: AsyncSession,
):
    await create_user(db_session)
    tokens = await login_user(client)

    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["refresh_token"]

    me_response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {body['access_token']}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "user@example.com"


async def test_refresh_rejects_access_token(
    client: AsyncClient,
    db_session: AsyncSession,
):
    await create_user(db_session)
    tokens = await login_user(client)

    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["access_token"]},
    )

    assert response.status_code == 401
    assert response.json() == {
        "message": "Invalid refresh token",
        "code": "invalid_refresh_token",
    }


@pytest.mark.parametrize(
    "refresh_token",
    [
        "not-a-jwt",
        make_token(user_id="not-a-uuid", token_type="refresh"),
        make_token(
            user_id="00000000-0000-0000-0000-000000000000",
            token_type="refresh",
        ),
        make_token(
            user_id="00000000-0000-0000-0000-000000000000",
            token_type="refresh",
            expires_delta=timedelta(seconds=-1),
        ),
    ],
)
async def test_refresh_rejects_invalid_refresh_tokens(
    client: AsyncClient,
    refresh_token: str,
):
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 401
    assert response.json() == {
        "message": "Invalid refresh token",
        "code": "invalid_refresh_token",
    }


async def test_refresh_rejects_inactive_user(
    client: AsyncClient,
    db_session: AsyncSession,
):
    inactive_user = await create_user(db_session, is_active=False)
    refresh_token = make_token(user_id=str(inactive_user.id), token_type="refresh")

    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 403
    assert response.json()["code"] == "inactive_user"


async def test_refresh_requires_refresh_token_field(client: AsyncClient):
    response = await client.post("/api/v1/auth/refresh", json={})

    assert response.status_code == 422
