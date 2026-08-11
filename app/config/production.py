"""AEGIS-Traffic — Production Settings"""

from app.config.base import BaseAppConfig


class ProductionConfig(BaseAppConfig):
    environment: str = "production"
    debug: bool = False
    db_echo: bool = False
    allowed_origins: list[str] = ["http://localhost:8501", "http://127.0.0.1:8501"]
