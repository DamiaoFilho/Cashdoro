from typing import Any

from fastapi.testclient import TestClient


def register_and_login(client: TestClient, email: str, username: str) -> tuple[Any, dict[str, str]]:
    user = client.post(
        "/api/v1/auth/register",
        json={"email": email, "username": username, "password": "s3cret-password"},
    ).json()
    tokens = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "s3cret-password"},
    ).json()
    return user, {"Authorization": f"Bearer {tokens['access_token']}"}


def test_user_only_accesses_their_own_cashdoro(client: TestClient) -> None:
    ana, ana_headers = register_and_login(client, "ana@example.com", "ana")
    bob, bob_headers = register_and_login(client, "bob@example.com", "bob")

    ana_cashdoro = client.get("/api/v1/cashdoro", headers=ana_headers).json()
    bob_cashdoro = client.get("/api/v1/cashdoro", headers=bob_headers).json()

    assert ana_cashdoro["user_id"] == ana["id"]
    assert bob_cashdoro["user_id"] == bob["id"]
    assert ana_cashdoro["id"] != bob_cashdoro["id"]

    bob_update = client.put(
        "/api/v1/cashdoro",
        headers=bob_headers,
        json={
            "session_time": 50,
            "pause_time": 10,
            "long_pause_time": 30,
            "sessions_until_long_break": 3,
            "hourly_rate": "12.50",
        },
    )

    assert bob_update.status_code == 200
    assert bob_update.json()["id"] == bob_cashdoro["id"]
    assert client.get("/api/v1/cashdoro", headers=ana_headers).json() == ana_cashdoro
