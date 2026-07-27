"""
AEGIS-Traffic — Centralized Configuration
All settings read from environment variables / .env file.
Supports SQLite (dev) and PostgreSQL (prod) via DATABASE_URL.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    # ── Application ──────────────────────────────────────────────
    app_name: str = "AEGIS-Traffic Secure Smart Intersection Engine"
    app_version: str = "8.0.0"
    debug: bool = False

    # ── Database ─────────────────────────────────────────────────
    # Set DATABASE_URL=postgresql://user:pass@host/db for production PostgreSQL
    database_url: str = Field(
        default="sqlite:///data/aegis_secure_vault.db",
        validation_alias="DATABASE_URL",
    )
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_echo: bool = False  # Set True to log all SQL statements

    # ── JWT / Auth ───────────────────────────────────────────────
    jwt_secret_key: str = Field(
        default="aegis-super-secret-jwt-key-change-in-production-998877",
        validation_alias="JWT_SECRET_KEY",
    )
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # ── Encryption ───────────────────────────────────────────────
    aegis_secret_key: str = Field(
        default="w21zdO8nX3jPcKFtyoHMmhquCU_sIf_bmra0Zl3A2L4=",
        validation_alias="AEGIS_SECRET_KEY",
    )

    # ── Security ─────────────────────────────────────────────────
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15
    password_min_length: int = 8

    # ── Rate Limiting ────────────────────────────────────────────
    rate_limit_per_minute: int = 60
    auth_rate_limit_per_minute: int = 10

    # ── CORS ─────────────────────────────────────────────────────
    allowed_origins: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """Returns cached settings singleton — call get_settings() everywhere."""
    return Settings()
