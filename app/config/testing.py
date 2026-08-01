"""AEGIS-Traffic — Testing Settings"""
from app.config.base import BaseAppConfig

class TestingConfig(BaseAppConfig):
    environment: str = "testing"
    debug: bool = True
    database_url: str = "sqlite:///:memory:"
    db_echo: bool = False
