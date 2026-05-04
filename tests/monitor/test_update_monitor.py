import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.monitor.helpers import (
    create_monitor_in_db,
    create_user_in_db,
    get_auth_headers,
)


async def test_update_monitor_name(
    client: AsyncClient,
    db_session: AsyncSession,
):
    user = await create_user_in_db(db_session, email="user@example.com")
    monitor = await create_monitor_in_db(db_session, user_id=user.id, name="Old Name")
    headers = await get_auth_headers(client, email="user@example.com")

    response = await client.patch(
        f"/api/v1/monitors/{monitor.id}",
        json={"name": "New Name"},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


async def test_update_monitor_url(
    client: AsyncClient,
    db_session: AsyncSession,
):
    user = await create_user_in_db(db_session, email="user@example.com")
    monitor = await create_monitor_in_db(
        db_session, user_id=user.id, url="https://old.example.com"
    )
    headers = await get_auth_headers(client, email="user@example.com")

    response = await client.patch(
        f"/api/v1/monitors/{monitor.id}",
        json={"url": "https://new.example.com"},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["url"] == "https://new.example.com/"


async def test_update_monitor_multiple_fields(
    client: AsyncClient,
    db_session: AsyncSession,
):
    user = await create_user_in_db(db_session, email="user@example.com")
    monitor = await create_monitor_in_db(db_session, user_id=user.id)
    headers = await get_auth_headers(client, email="user@example.com")

    response = await client.patch(
        f"/api/v1/monitors/{monitor.id}",
        json={
            "name": "Updated",
            "check_interval": 300,
            "timeout": 30,
            "expected_status": 201,
            "is_active": False,
        },
        headers=headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Updated"
    assert body["check_interval"] == 300
    assert body["timeout"] == 30
    assert body["expected_status"] == 201
    assert body["is_active"] is False


async def test_update_monitor_empty_body_returns_unchanged_monitor(
    client: AsyncClient,
    db_session: AsyncSession,
):
    user = await create_user_in_db(db_session, email="user@example.com")
    monitor = await create_monitor_in_db(
        db_session, user_id=user.id, name="Original Name"
    )
    headers = await get_auth_headers(client, email="user@example.com")

    response = await client.patch(
        f"/api/v1/monitors/{monitor.id}",
        json={},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Original Name"


async def test_update_monitor_not_found(
    client: AsyncClient,
    db_session: AsyncSession,
):
    await create_user_in_db(db_session, email="user@example.com")
    headers = await get_auth_headers(client, email="user@example.com")

    response = await client.patch(
        f"/api/v1/monitors/{uuid.uuid4()}",
        json={"name": "New Name"},
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json() == {
        "message": "Monitor not found",
        "code": "monitor_not_found",
    }


async def test_update_monitor_returns_404_for_other_users_monitor(
    client: AsyncClient,
    db_session: AsyncSession,
):
    user_a = await create_user_in_db(db_session, email="a@example.com")
    await create_user_in_db(db_session, email="b@example.com")
    monitor = await create_monitor_in_db(db_session, user_id=user_a.id)

    headers = await get_auth_headers(client, email="b@example.com")
    response = await client.patch(
        f"/api/v1/monitors/{monitor.id}",
        json={"name": "Stolen Name"},
        headers=headers,
    )

    assert response.status_code == 404


async def test_update_monitor_requires_authentication(
    client: AsyncClient,
    db_session: AsyncSession,
):
    user = await create_user_in_db(db_session, email="user@example.com")
    monitor = await create_monitor_in_db(db_session, user_id=user.id)

    response = await client.patch(
        f"/api/v1/monitors/{monitor.id}",
        json={"name": "New Name"},
    )

    assert response.status_code == 401


@pytest.mark.parametrize(
    "payload",
    [
        {"name": ""},
        {"name": "A" * 256},
        {"url": "not-a-url"},
        {"check_interval": 0},
        {"check_interval": 86401},
        {"timeout": 0},
        {"timeout": 61},
        {"expected_status": 99},
        {"expected_status": 600},
        {"unknown_field": "value"},
    ],
)
async def test_update_monitor_validation_errors(
    client: AsyncClient,
    db_session: AsyncSession,
    payload: dict,
):
    user = await create_user_in_db(db_session, email="user@example.com")
    monitor = await create_monitor_in_db(db_session, user_id=user.id)
    headers = await get_auth_headers(client, email="user@example.com")

    response = await client.patch(
        f"/api/v1/monitors/{monitor.id}",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 422
