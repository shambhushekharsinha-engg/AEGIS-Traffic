"""
AEGIS-Traffic — Configuration Entrypoint
Re-exports from modular app.config package.
"""

from app.config import Settings, get_settings

__all__ = ["get_settings", "Settings"]
