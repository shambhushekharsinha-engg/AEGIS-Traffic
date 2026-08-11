"""
AEGIS-Traffic — Caching Utilities
Provides cached helper wrappers for heavy operations (Geo lookup, Weather API, AegisClient instance).
"""

from typing import Any, Dict

import streamlit as st

from dashboard.services.api import AegisClient
from dashboard.services.logger import logger


def get_api_client() -> AegisClient:
    """Returns instance of AegisClient."""
    logger.info("Initializing AegisClient...")
    return AegisClient()


@st.cache_data(ttl=300)
def cached_geo_sync(location_name: str, lat: float, lon: float) -> Dict[str, Any]:
    """Caches geo-currency context lookup for 5 minutes."""
    try:
        from app.core.geo_currency import detect_country, get_country_config

        cc = detect_country(
            location_name=location_name, lat=lat, lon=lon, try_nominatim=True
        )
        cfg = get_country_config(cc)
        return {
            "country_code": cc,
            "country_flag": cfg["flag"],
            "country_name": cfg["name"],
            "currency_code": cfg["currency_code"],
            "currency_symbol": cfg["currency_symbol"],
            "speed_limit_kmh": cfg.get("speed_limit_urban", 50),
            "drive_side": cfg.get("drive_side", "right"),
            "plate_format": cfg.get("plate_format", ""),
        }
    except Exception as e:
        logger.warning(f"Geo sync fallback triggered: {e}")
        return {
            "country_code": "IN",
            "country_flag": "🇮🇳",
            "country_name": "India",
            "currency_code": "INR",
            "currency_symbol": "₹",
            "speed_limit_kmh": 50,
            "drive_side": "left",
            "plate_format": "XX00 XX0000",
        }
