"""
AEGIS-Traffic — Configuration Entrypoint
Re-exports from modular app.config package.
"""

from app.config import get_settings, Settings

__all__ = ["get_settings", "Settings"]
