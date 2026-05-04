import uuid

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.monitor.helpers import (
    create_monitor_in_db,
    create_user_in_db,
    get_auth_headers,
)


async def test_get_monitor_by_id_success(
    client: AsyncClient,
    db_session: AsyncSession,
):
    user = await create_user_in_db(db_session, email="user@example.com")
    monitor = await create_monitor_in_db(
        db_session,
        user_id=user.id,
        name="My Monitor",
        url="https://example.com",
    )
    headers = await get_auth_headers(client, email="user@example.com")

    response = await client.get(f"/api/v1/monitors/{monitor.id}", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(monitor.id)
    assert body["name"] == "My Monitor"
    assert body["url"] == "https://example.com/"
    assert body["user_id"] == str(user.id)


async def test_get_monitor_by_id_not_found(
    client: AsyncClient,
    db_session: AsyncSession,
):
    await create_user_in_db(db_session, email="user@example.com")
    headers = await get_auth_headers(client, email="user@example.com")

    response = await client.get(f"/api/v1/monitors/{uuid.uuid4()}", headers=headers)

    assert response.status_code == 404
    assert response.json() == {
        "message": "Monitor not found",
        "code": "monitor_not_found",
    }


async def test_get_monitor_by_id_returns_404_for_other_users_monitor(
    client: AsyncClient,
    db_session: AsyncSession,
):
    user_a = await create_user_in_db(db_session, email="a@example.com")
    await create_user_in_db(db_session, email="b@example.com")
    monitor = await create_monitor_in_db(db_session, user_id=user_a.id)

    headers = await get_auth_headers(client, email="b@example.com")
    response = await client.get(f"/api/v1/monitors/{monitor.id}", headers=headers)

    assert response.status_code == 404


async def test_get_monitor_by_id_requires_authentication(
    client: AsyncClient,
    db_session: AsyncSession,
):
    user = await create_user_in_db(db_session, email="user@example.com")
    monitor = await create_monitor_in_db(db_session, user_id=user.id)

    response = await client.get(f"/api/v1/monitors/{monitor.id}")

    assert response.status_code == 401


async def test_get_monitor_by_id_invalid_uuid(
    client: AsyncClient,
    db_session: AsyncSession,
):
    await create_user_in_db(db_session, email="user@example.com")
    headers = await get_auth_headers(client, email="user@example.com")

    response = await client.get("/api/v1/monitors/not-a-uuid", headers=headers)

    assert response.status_code == 422
