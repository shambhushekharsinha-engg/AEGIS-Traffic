"""AEGIS-Traffic — Development Settings"""
from app.config.base import BaseAppConfig

class DevelopmentConfig(BaseAppConfig):
    environment: str = "development"
    debug: bool = True
    db_echo: bool = True
