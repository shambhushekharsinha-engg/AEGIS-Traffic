"""
AEGIS-Traffic — Centralized Settings Factory
Loads environment-specific configuration based on AEGIS_ENV environment variable.
"""

import os
from functools import lru_cache

from app.config.base import BaseAppConfig
from app.config.development import DevelopmentConfig
from app.config.production import ProductionConfig
from app.config.testing import TestingConfig

# Re-export Settings for backwards compatibility
Settings = BaseAppConfig


@lru_cache()
def get_settings() -> BaseAppConfig:
    env = os.environ.get("AEGIS_ENV", "development").lower()
    if env == "production":
        return ProductionConfig()
    elif env == "testing":
        return TestingConfig()
    return DevelopmentConfig()
