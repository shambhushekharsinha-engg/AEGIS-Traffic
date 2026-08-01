"""
AEGIS-Traffic — Smart City Operations Dashboard (Refactored Main Entrypoint)
Modular controller handling routing, session state, theme injection, and authentication gate.
"""
import sys
import os

# Ensure root directory is on Python path for app/ imports if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import uuid
import streamlit as st

from dashboard.theme.theme import inject_theme
from dashboard.services.cache import get_api_client, cached_geo_sync
from dashboard.services.logger import logger
from dashboard.components.widgets import render_login_portal
from dashboard.components.navbar import render_navbar
from dashboard.components.sidebar import render_sidebar

# Import Page Modules
from dashboard.pages.overview import render_overview_page
from dashboard.pages.analytics import render_analytics_page
from dashboard.pages.maps import render_maps_page
from dashboard.pages.violations import render_violations_page
from dashboard.pages.anpr import render_anpr_page
from dashboard.pages.copilot import render_copilot_page
from dashboard.pages.reports import render_reports_page
from dashboard.pages.admin import render_admin_page
from dashboard.pages.settings import render_settings_page
from dashboard.pages.citizen import render_citizen_page
from dashboard.pages.guide import render_guide_page


# ── Page Config ──
st.set_page_config(
    page_title="AEGIS-TRAFFIC // Smart City Operations",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Theme Injection ──
inject_theme()

# ── API Client Instance ──
client = get_api_client()

# ── Session State Bootstrap ──
for key, default in [
    ("user_token", f"AEGIS-{uuid.uuid4().hex[:8].upper()}"),
    ("chat_history", []),
    ("copilot_history", []),
    ("latitude", 28.6315),
    ("longitude", 77.2167),
    ("location_name", "Connaught Place, New Delhi"),
    ("active_data", None),
    ("country_code", "IN"),
    ("country_flag", "🇮🇳"),
    ("country_name", "India"),
    ("currency_code", "INR"),
    ("currency_symbol", "₹"),
    ("speed_limit_kmh", 50),
    ("drive_side", "left"),
    ("plate_format", "XX00 XX0000"),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# Sync Geo Context via cached helper
geo_cfg = cached_geo_sync(st.session_state.location_name, st.session_state.latitude, st.session_state.longitude)
for k, v in geo_cfg.items():
    st.session_state[k] = v

# ── Authentication Gatekeeper ──
if "jwt_token" not in st.session_state:
    render_login_portal(client, on_login_success=lambda: st.rerun())
    st.stop()

# ── Authenticated Application Layout ──
render_navbar(client)
render_sidebar()

PAGE_ROUTER = {
    "📊 Operations HUD": render_overview_page,
    "📈 Predictive Analytics": render_analytics_page,
    "🌍 Map Intelligence": render_maps_page,
    "🤖 AI Copilot": render_copilot_page,
    "🚘 ANPR & Violations": render_violations_page,
    "📑 Reports & Exports": render_reports_page,
    "👥 Public Citizen Portal": render_citizen_page,
    "📚 Learning Guide": render_guide_page,
    "🛡️ Audit & Security": render_admin_page,
    "⚙️ Settings & Pipeline": render_settings_page,
}

current_page = st.session_state.get("current_page", "📊 Operations HUD")
render_func = PAGE_ROUTER.get(current_page, render_overview_page)
render_func(client)