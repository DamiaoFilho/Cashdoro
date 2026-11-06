import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, make_url, text

from src.main import create_app
from src.shared.config import get_settings

TEST_DB_NAME = "cashdoro_test"
ALEMBIC_INI = Path(__file__).parents[1] / "alembic.ini"

# Tests must never touch the development database. The app lifespan and Alembic read the database
# name from get_settings(), which is first called inside the fixtures below.
os.environ["DB_NAME"] = TEST_DB_NAME
os.environ["JWT_SECRET"] = "test-only-secret-with-at-least-32-bytes"


@pytest.fixture(scope="session")
def test_engine() -> Iterator[Engine]:
    database_url = make_url(get_settings().database_url)

    admin_engine = create_engine(
        database_url.set(database="postgres"), isolation_level="AUTOCOMMIT"
    )
    with admin_engine.connect() as connection:
        exists = connection.scalar(
            text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": TEST_DB_NAME}
        )
        if not exists:
            connection.execute(text(f'CREATE DATABASE "{TEST_DB_NAME}"'))
    admin_engine.dispose()

    command.upgrade(Config(str(ALEMBIC_INI)), "head")

    engine = create_engine(database_url)
    yield engine
    engine.dispose()


@pytest.fixture(autouse=True)
def clean_database(test_engine: Engine) -> Iterator[None]:
    yield
    with test_engine.begin() as connection:
        tables = connection.scalars(
            text(
                "SELECT tablename FROM pg_tables "
                "WHERE schemaname = 'public' AND tablename <> 'alembic_version'"
            )
        ).all()
        if tables:
            table_list = ", ".join(f'"{table}"' for table in tables)
            connection.execute(text(f"TRUNCATE {table_list} CASCADE"))


@pytest.fixture
def client() -> Iterator[TestClient]:
    # The context manager runs the app lifespan (engine and session factory setup/teardown).
    with TestClient(create_app()) as test_client:
        yield test_client
