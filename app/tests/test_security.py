"""
AEGIS-Traffic — Security & Configuration Tests
Tests security middleware response headers, JWT auth verification, and multi-environment settings.
"""

import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_security_headers_present(client):
    """Verifies that SecurityHeadersMiddleware attaches mandatory security response headers."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Content-Security-Policy" in response.headers
    assert "Strict-Transport-Security" in response.headers
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-Content-Type-Options") == "nosniff"


def test_config_environment_loading():
    """Verifies configuration settings loader returns valid BaseAppConfig instance."""
    settings = get_settings()
    assert settings.app_name is not None
    assert settings.access_token_expire_minutes > 0
    assert settings.jwt_secret_key is not None


def test_invalid_login_denied(client):
    """Verifies authentication failure for non-existent user credentials."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "nonexistent_user", "password": "WrongPassword123!"},
    )
    assert response.status_code == 401
