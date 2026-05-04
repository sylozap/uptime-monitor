import uuid

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.monitor.helpers import (
    create_monitor_in_db,
    create_user_in_db,
    get_auth_headers,
)


async def test_delete_monitor_success(
    client: AsyncClient,
    db_session: AsyncSession,
):
    user = await create_user_in_db(db_session, email="user@example.com")
    monitor = await create_monitor_in_db(db_session, user_id=user.id)
    headers = await get_auth_headers(client, email="user@example.com")

    response = await client.delete(f"/api/v1/monitors/{monitor.id}", headers=headers)

    assert response.status_code == 204
    assert response.content == b""


async def test_delete_monitor_is_no_longer_accessible_after_deletion(
    client: AsyncClient,
    db_session: AsyncSession,
):
    user = await create_user_in_db(db_session, email="user@example.com")
    monitor = await create_monitor_in_db(db_session, user_id=user.id)
    headers = await get_auth_headers(client, email="user@example.com")

    await client.delete(f"/api/v1/monitors/{monitor.id}", headers=headers)
    get_response = await client.get(f"/api/v1/monitors/{monitor.id}", headers=headers)

    assert get_response.status_code == 404


async def test_delete_monitor_not_found(
    client: AsyncClient,
    db_session: AsyncSession,
):
    await create_user_in_db(db_session, email="user@example.com")
    headers = await get_auth_headers(client, email="user@example.com")

    response = await client.delete(f"/api/v1/monitors/{uuid.uuid4()}", headers=headers)

    assert response.status_code == 404
    assert response.json() == {
        "message": "Monitor not found",
        "code": "monitor_not_found",
    }


async def test_delete_monitor_returns_404_for_other_users_monitor(
    client: AsyncClient,
    db_session: AsyncSession,
):
    user_a = await create_user_in_db(db_session, email="a@example.com")
    await create_user_in_db(db_session, email="b@example.com")
    monitor = await create_monitor_in_db(db_session, user_id=user_a.id)

    headers_b = await get_auth_headers(client, email="b@example.com")
    response = await client.delete(f"/api/v1/monitors/{monitor.id}", headers=headers_b)

    assert response.status_code == 404

    headers_a = await get_auth_headers(client, email="a@example.com")
    get_response = await client.get(f"/api/v1/monitors/{monitor.id}", headers=headers_a)
    assert get_response.status_code == 200


async def test_delete_monitor_requires_authentication(
    client: AsyncClient,
    db_session: AsyncSession,
):
    user = await create_user_in_db(db_session, email="user@example.com")
    monitor = await create_monitor_in_db(db_session, user_id=user.id)

    response = await client.delete(f"/api/v1/monitors/{monitor.id}")

    assert response.status_code == 401


async def test_delete_monitor_invalid_uuid(
    client: AsyncClient,
    db_session: AsyncSession,
):
    await create_user_in_db(db_session, email="user@example.com")
    headers = await get_auth_headers(client, email="user@example.com")

    response = await client.delete("/api/v1/monitors/not-a-uuid", headers=headers)

    assert response.status_code == 422
