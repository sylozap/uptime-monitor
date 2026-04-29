import pytest
from httpx import AsyncClient


async def test_register_user_success(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "User@Example.com", "password": "secret123"},
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": response.json()["id"],
        "email": "user@example.com",
    }
    assert "password" not in response.json()
    assert "hashed_password" not in response.json()


async def test_register_duplicate_email_returns_conflict(client: AsyncClient):
    payload = {"email": "user@example.com", "password": "secret123"}

    first_response = await client.post("/api/v1/auth/register", json=payload)
    second_response = await client.post("/api/v1/auth/register", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json() == {
        "message": "User with this email already exists",
        "code": "user_already_exists",
    }


async def test_register_duplicate_email_is_case_insensitive(client: AsyncClient):
    first_response = await client.post(
        "/api/v1/auth/register",
        json={"email": "user@example.com", "password": "secret123"},
    )
    second_response = await client.post(
        "/api/v1/auth/register",
        json={"email": "USER@example.com", "password": "secret123"},
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["code"] == "user_already_exists"


@pytest.mark.parametrize(
    ("payload", "expected_status"),
    [
        ({"email": "not-an-email", "password": "secret123"}, 422),
        ({"email": "user@example.com", "password": "short"}, 422),
        ({"password": "secret123"}, 422),
        ({"email": "user@example.com"}, 422),
    ],
)
async def test_register_validation_errors(
    client: AsyncClient,
    payload: dict[str, str],
    expected_status: int,
):
    response = await client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == expected_status
