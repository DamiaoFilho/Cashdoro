from fastapi.testclient import TestClient


def test_register_creates_default_cashdoro(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/register",
        json={"email": "ana@example.com", "username": "ana", "password": "s3cret-password"},
    )
    tokens = client.post(
        "/api/v1/auth/login",
        data={"username": "ana@example.com", "password": "s3cret-password"},
    ).json()

    response = client.get(
        "/api/v1/cashdoro",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["session_time"] == 25
    assert body["pause_time"] == 5
    assert body["long_pause_time"] == 15
    assert body["sessions_until_long_break"] == 4
    assert body["hourly_rate"] is None
    assert body["total_earnings"] == "0.00"
