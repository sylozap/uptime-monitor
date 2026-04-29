import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.auth.helpers import create_user


async def test_login_success_returns_token_pair(
    client: AsyncClient,
    db_session: AsyncSession,
):
    await create_user(db_session, email="user@example.com", password="secret123")

    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "USER@example.com", "password": "secret123"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["access_token"] != body["refresh_token"]


@pytest.mark.parametrize(
    ("email", "password"),
    [
        ("missing@example.com", "secret123"),
        ("user@example.com", "wrong-password"),
    ],
)
async def test_login_invalid_credentials_return_generic_error(
    client: AsyncClient,
    db_session: AsyncSession,
    email: str,
    password: str,
):
    await create_user(db_session, email="user@example.com", password="secret123")

    response = await client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )

    assert response.status_code == 401
    assert response.json() == {
        "message": "Invalid email or password",
        "code": "invalid_credentials",
    }


async def test_login_inactive_user_returns_forbidden(
    client: AsyncClient,
    db_session: AsyncSession,
):
    await create_user(
        db_session,
        email="inactive@example.com",
        password="secret123",
        is_active=False,
    )

    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "inactive@example.com", "password": "secret123"},
    )

    assert response.status_code == 403
    assert response.json() == {
        "message": "User account is inactive",
        "code": "inactive_user",
    }
