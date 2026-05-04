from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.monitor.helpers import (
    create_monitor_in_db,
    create_user_in_db,
    get_auth_headers,
)


async def test_get_monitors_returns_empty_list(
    client: AsyncClient,
    db_session: AsyncSession,
):
    await create_user_in_db(db_session, email="user@example.com")
    headers = await get_auth_headers(client, email="user@example.com")

    response = await client.get("/api/v1/monitors/", headers=headers)

    assert response.status_code == 200
    assert response.json() == []


async def test_get_monitors_returns_own_monitors(
    client: AsyncClient,
    db_session: AsyncSession,
):
    user = await create_user_in_db(db_session, email="user@example.com")
    await create_monitor_in_db(db_session, user_id=user.id, name="Monitor 1")
    await create_monitor_in_db(db_session, user_id=user.id, name="Monitor 2")
    headers = await get_auth_headers(client, email="user@example.com")

    response = await client.get("/api/v1/monitors/", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    names = {m["name"] for m in body}
    assert names == {"Monitor 1", "Monitor 2"}


async def test_get_monitors_does_not_return_other_users_monitors(
    client: AsyncClient,
    db_session: AsyncSession,
):
    user_a = await create_user_in_db(db_session, email="a@example.com")
    user_b = await create_user_in_db(db_session, email="b@example.com")
    await create_monitor_in_db(db_session, user_id=user_a.id, name="A's Monitor")
    await create_monitor_in_db(db_session, user_id=user_b.id, name="B's Monitor")

    headers = await get_auth_headers(client, email="a@example.com")
    response = await client.get("/api/v1/monitors/", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["name"] == "A's Monitor"


async def test_get_monitors_pagination_limit(
    client: AsyncClient,
    db_session: AsyncSession,
):
    user = await create_user_in_db(db_session, email="user@example.com")
    for i in range(5):
        await create_monitor_in_db(db_session, user_id=user.id, name=f"Monitor {i}")
    headers = await get_auth_headers(client, email="user@example.com")

    response = await client.get("/api/v1/monitors/?limit=3", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 3


async def test_get_monitors_pagination_offset(
    client: AsyncClient,
    db_session: AsyncSession,
):
    user = await create_user_in_db(db_session, email="user@example.com")
    for i in range(5):
        await create_monitor_in_db(db_session, user_id=user.id, name=f"Monitor {i}")
    headers = await get_auth_headers(client, email="user@example.com")

    all_response = await client.get("/api/v1/monitors/?limit=100", headers=headers)
    all_ids = [m["id"] for m in all_response.json()]

    offset_response = await client.get(
        "/api/v1/monitors/?limit=100&offset=2", headers=headers
    )
    offset_ids = [m["id"] for m in offset_response.json()]

    assert len(offset_ids) == 3
    assert offset_ids == all_ids[2:]


async def test_get_monitors_requires_authentication(client: AsyncClient):
    response = await client.get("/api/v1/monitors/")

    assert response.status_code == 401


async def test_get_monitors_invalid_pagination_params(
    client: AsyncClient,
    db_session: AsyncSession,
):
    await create_user_in_db(db_session, email="user@example.com")
    headers = await get_auth_headers(client, email="user@example.com")

    response = await client.get("/api/v1/monitors/?limit=0", headers=headers)
    assert response.status_code == 422

    response = await client.get("/api/v1/monitors/?limit=101", headers=headers)
    assert response.status_code == 422

    response = await client.get("/api/v1/monitors/?offset=-1", headers=headers)
    assert response.status_code == 422
