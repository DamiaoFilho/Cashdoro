from fastapi.testclient import TestClient


def test_get_me_returns_logged_in_user(client: TestClient) -> None:
    registered = client.post(
        "/api/v1/auth/register",
        json={"email": "ana@example.com", "username": "ana", "password": "s3cret-password"},
    ).json()
    tokens = client.post(
        "/api/v1/auth/login",
        data={"username": "ana@example.com", "password": "s3cret-password"},
    ).json()

    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == registered["id"]
    assert body["email"] == "ana@example.com"
    assert body["username"] == "ana"
    assert body["is_active"] is True
    assert body["is_verified"] is False
    assert "password" not in body
    assert "password_hash" not in body


def test_get_me_requires_login(client: TestClient) -> None:
    response = client.get("/api/v1/users/me")

    assert response.status_code == 401
