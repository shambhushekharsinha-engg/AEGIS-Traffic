"""
AEGIS-Traffic — Pytest Global Test Fixtures
Ensures SQLite database tables and default seed accounts exist before any test runs.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import create_tables, get_db
from app.db import crud


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Session-wide fixture ensuring database tables and default users exist."""
    create_tables()
    db = next(get_db())
    try:
        crud.seed_default_users(db)
    finally:
        db.close()


@pytest.fixture
def client(setup_test_database):
    """Yields FastAPI TestClient wrapped in lifespan context."""
    with TestClient(app) as c:
        yield c
