import pytest
from fastapi.testclient import TestClient


def test_update_cashdoro_changes_settings(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/register",
        json={"email": "ana@example.com", "username": "ana", "password": "s3cret-password"},
    )
    tokens = client.post(
        "/api/v1/auth/login",
        data={"username": "ana@example.com", "password": "s3cret-password"},
    ).json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    response = client.put(
        "/api/v1/cashdoro",
        headers=headers,
        json={
            "session_time": 50,
            "pause_time": 10,
            "long_pause_time": 30,
            "sessions_until_long_break": 3,
            "hourly_rate": "12.50",
        },
    )

    assert response.status_code == 200
    expected = {
        "session_time": 50,
        "pause_time": 10,
        "long_pause_time": 30,
        "sessions_until_long_break": 3,
        "hourly_rate": "12.50",
        "total_earnings": "0.00",
    }
    assert response.json().items() >= expected.items()
    fetched = client.get("/api/v1/cashdoro", headers=headers).json()
    assert fetched.items() >= expected.items()


@pytest.mark.parametrize("session_time", ["a", "abc", "", None, 1.5, 0, 181])
def test_update_cashdoro_rejects_invalid_session_time(
    client: TestClient, session_time: object
) -> None:
    client.post(
        "/api/v1/auth/register",
        json={"email": "ana@example.com", "username": "ana", "password": "s3cret-password"},
    )
    tokens = client.post(
        "/api/v1/auth/login",
        data={"username": "ana@example.com", "password": "s3cret-password"},
    ).json()

    response = client.put(
        "/api/v1/cashdoro",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
        json={
            "session_time": session_time,
            "pause_time": 10,
            "long_pause_time": 30,
            "sessions_until_long_break": 3,
            "hourly_rate": "12.50",
        },
    )

    assert response.status_code == 422
