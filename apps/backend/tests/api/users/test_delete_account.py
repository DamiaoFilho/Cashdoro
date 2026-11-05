from fastapi.testclient import TestClient


def test_delete_account_removes_access(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/register",
        json={"email": "ana@example.com", "username": "ana", "password": "s3cret-password"},
    )
    tokens = client.post(
        "/api/v1/auth/login",
        data={"username": "ana@example.com", "password": "s3cret-password"},
    ).json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    response = client.delete("/api/v1/users/me", headers=headers)

    assert response.status_code == 204
    assert client.get("/api/v1/users/me", headers=headers).status_code == 401
