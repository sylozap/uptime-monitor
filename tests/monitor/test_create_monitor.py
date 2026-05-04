import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.monitor.helpers import create_user_in_db, get_auth_headers


async def test_create_monitor_success(
    client: AsyncClient,
    db_session: AsyncSession,
):
    user = await create_user_in_db(db_session, email="user@example.com")
    headers = await get_auth_headers(client, email="user@example.com")

    response = await client.post(
        "/api/v1/monitors/",
        json={
            "name": "My Site",
            "url": "https://example.com",
            "check_interval": 120,
            "timeout": 15,
            "expected_status": 200,
            "is_active": True,
        },
        headers=headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "My Site"
    assert body["url"] == "https://example.com/"
    assert body["check_interval"] == 120
    assert body["timeout"] == 15
    assert body["expected_status"] == 200
    assert body["is_active"] is True
    assert body["user_id"] == str(user.id)
    assert body["last_status"] is None
    assert body["last_status_code"] is None
    assert body["last_checked_at"] is None
    assert "id" in body
    assert "created_at" in body
    assert "updated_at" in body


async def test_create_monitor_uses_defaults(
    client: AsyncClient,
    db_session: AsyncSession,
):
    await create_user_in_db(db_session, email="user@example.com")
    headers = await get_auth_headers(client, email="user@example.com")

    response = await client.post(
        "/api/v1/monitors/",
        json={"name": "Minimal Monitor", "url": "https://example.com"},
        headers=headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["check_interval"] == 60
    assert body["timeout"] == 10
    assert body["expected_status"] == 200
    assert body["is_active"] is True


async def test_create_monitor_requires_authentication(client: AsyncClient):
    response = await client.post(
        "/api/v1/monitors/",
        json={"name": "My Site", "url": "https://example.com"},
    )

    assert response.status_code == 401


@pytest.mark.parametrize(
    "payload",
    [
        {"name": "", "url": "https://example.com"},
        {"name": "A" * 256, "url": "https://example.com"},
        {"name": "My Monitor", "url": "not-a-url"},
        {"name": "My Monitor", "url": "https://example.com", "check_interval": 0},
        {"name": "My Monitor", "url": "https://example.com", "check_interval": 86401},
        {"name": "My Monitor", "url": "https://example.com", "timeout": 0},
        {"name": "My Monitor", "url": "https://example.com", "timeout": 61},
        {"name": "My Monitor", "url": "https://example.com", "expected_status": 99},
        {"name": "My Monitor", "url": "https://example.com", "expected_status": 600},
        {"url": "https://example.com"},
        {"name": "My Monitor"},
        {"name": "My Monitor", "url": "https://example.com", "extra_field": "value"},
    ],
)
async def test_create_monitor_validation_errors(
    client: AsyncClient,
    db_session: AsyncSession,
    payload: dict,
):
    await create_user_in_db(db_session, email="user@example.com")
    headers = await get_auth_headers(client, email="user@example.com")

    response = await client.post("/api/v1/monitors/", json=payload, headers=headers)

    assert response.status_code == 422
