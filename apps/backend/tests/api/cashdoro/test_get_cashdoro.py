from fastapi.testclient import TestClient
from sqlalchemy import Engine, text

# Only the failure case lives here: test_default_cashdoro.py already covers the successful fetch.


def test_get_cashdoro_returns_404_when_user_has_no_cashdoro(
    client: TestClient, test_engine: Engine
) -> None:
    client.post(
        "/api/v1/auth/register",
        json={"email": "ana@example.com", "username": "ana", "password": "s3cret-password"},
    )
    tokens = client.post(
        "/api/v1/auth/login",
        data={"username": "ana@example.com", "password": "s3cret-password"},
    ).json()
    # Register always creates a cashdoro and the API can't delete one, so remove it directly.
    with test_engine.begin() as connection:
        connection.execute(text("DELETE FROM cashdoros"))

    response = client.get(
        "/api/v1/cashdoro",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Cashdoro not found"
