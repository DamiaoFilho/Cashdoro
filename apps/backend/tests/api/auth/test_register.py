import pytest
from fastapi.testclient import TestClient


def test_register_creates_active_unverified_user(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "ana@example.com", "username": "ana", "password": "s3cret-password"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"]
    assert body["email"] == "ana@example.com"
    assert body["username"] == "ana"
    assert body["is_active"] is True
    assert body["is_verified"] is False
    assert "password" not in body
    assert "password_hash" not in body


@pytest.mark.parametrize("email", ["not-an-email", "ana@", "@example.com", ""])
def test_register_rejects_invalid_email(client: TestClient, email: str) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "username": "ana", "password": "s3cret-password"},
    )

    assert response.status_code == 422


@pytest.mark.parametrize("username", ["a", "a" * 50])
def test_register_accepts_username_within_length_limits(client: TestClient, username: str) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "ana@example.com", "username": username, "password": "s3cret-password"},
    )

    assert response.status_code == 201
    assert response.json()["username"] == username


@pytest.mark.parametrize("username", ["", "   ", "a" * 51])
def test_register_rejects_username_outside_length_limits(client: TestClient, username: str) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "ana@example.com", "username": username, "password": "s3cret-password"},
    )

    assert response.status_code == 422


def test_register_strips_surrounding_whitespace_from_username(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "ana@example.com", "username": "  ana  ", "password": "s3cret-password"},
    )

    assert response.status_code == 201
    assert response.json()["username"] == "ana"
