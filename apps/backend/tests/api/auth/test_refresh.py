from fastapi.testclient import TestClient


def register_and_login(client: TestClient) -> dict[str, str]:
    client.post(
        "/api/v1/auth/register",
        json={"email": "ana@example.com", "username": "ana", "password": "s3cret-password"},
    )
    return client.post(
        "/api/v1/auth/login",
        data={"username": "ana@example.com", "password": "s3cret-password"},
    ).json()


def test_refresh_returns_new_working_token_pair(client: TestClient) -> None:
    tokens = register_and_login(client)

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )

    assert response.status_code == 200
    new_tokens = response.json()
    assert new_tokens["token_type"] == "bearer"
    assert new_tokens["refresh_token"] != tokens["refresh_token"]
    me = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {new_tokens['access_token']}"},
    )
    assert me.status_code == 200
    assert me.json()["email"] == "ana@example.com"


def test_refresh_revokes_the_old_token(client: TestClient) -> None:
    tokens = register_and_login(client)
    client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )

    assert response.status_code == 401
