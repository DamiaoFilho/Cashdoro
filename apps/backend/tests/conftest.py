from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from src.main import create_app


@pytest.fixture
def client() -> Iterator[TestClient]:
    # The context manager runs the app lifespan (engine and session factory setup/teardown).
    with TestClient(create_app()) as test_client:
        yield test_client
