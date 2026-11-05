from fastapi.testclient import TestClient


def test_logout_revokes_the_refresh_token(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/register",
        json={"email": "ana@example.com", "username": "ana", "password": "s3cret-password"},
    )
    tokens = client.post(
        "/api/v1/auth/login",
        data={"username": "ana@example.com", "password": "s3cret-password"},
    ).json()

    response = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": tokens["refresh_token"]},
    )

    assert response.status_code == 204
    refresh = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refresh.status_code == 401
