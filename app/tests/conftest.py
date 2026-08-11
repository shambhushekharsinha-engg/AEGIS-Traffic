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


from unittest.mock import patch, MagicMock


@pytest.fixture(autouse=True)
def mock_celery_task():
    with patch("app.worker.analyze_traffic_task.delay") as mock_delay:
        mock_task = MagicMock()
        mock_task.id = "test-task-1234"
        mock_delay.return_value = mock_task
        yield mock_delay


@pytest.fixture(autouse=True)
def mock_celery_result():
    with patch("celery.result.AsyncResult") as mock_result_class:
        mock_result = MagicMock()
        mock_result.state = "SUCCESS"
        mock_result.result = {"mock_result": True}
        mock_result_class.return_value = mock_result
        yield mock_result_class
