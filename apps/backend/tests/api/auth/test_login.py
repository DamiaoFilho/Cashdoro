import pytest
from fastapi.testclient import TestClient


def test_login_returns_token_pair(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/register",
        json={"email": "ana@example.com", "username": "ana", "password": "s3cret-password"},
    )

    response = client.post(
        "/api/v1/auth/login",
        data={"username": "ana@example.com", "password": "s3cret-password"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["token_type"] == "bearer"


def test_login_accepts_email_as_typed_at_registration(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/register",
        json={"email": "Ana@Example.COM", "username": "ana", "password": "s3cret-password"},
    )

    response = client.post(
        "/api/v1/auth/login",
        data={"username": "Ana@Example.COM", "password": "s3cret-password"},
    )

    assert response.status_code == 200


@pytest.mark.parametrize(
    "data",
    [
        pytest.param({"password": "s3cret-password"}, id="email-missing"),
        pytest.param({"username": "", "password": "s3cret-password"}, id="email-empty"),
        pytest.param({"username": "ana@example.com"}, id="password-missing"),
        pytest.param({"username": "ana@example.com", "password": ""}, id="password-empty"),
    ],
)
def test_login_requires_email_and_password(client: TestClient, data: dict[str, str]) -> None:
    client.post(
        "/api/v1/auth/register",
        json={"email": "ana@example.com", "username": "ana", "password": "s3cret-password"},
    )

    response = client.post("/api/v1/auth/login", data=data)

    assert response.status_code == 422
