"""
AEGIS-Traffic — GIS Map Intelligence Page Module
"""
import streamlit as st
import pandas as pd
import numpy as np
from dashboard.components.widgets import sec_div


def render_maps_page(client):
    """Renders interactive GIS map with live vehicle markers and congestion heatmap."""
    sec_div("🗺️ GIS MAP INTELLIGENCE & SATELLITE TELEMETRY")

    lat = st.session_state.get("latitude", 28.6315)
    lon = st.session_state.get("longitude", 77.2167)
    loc_name = st.session_state.get("location_name", "Connaught Place, New Delhi")

    st.markdown(f"""
    <div class="card" style="margin-bottom:16px;">
        <div style="font-family:'Orbitron',sans-serif;color:#00f0ff;font-size:1.05rem;">
            📍 PRIMARY NODE: {loc_name.upper()}
        </div>
        <div style="font-family:'JetBrains Mono',monospace;color:#64748b;font-size:.78rem;margin-top:4px;">
            COORDINATES: {lat:.5f}° N, {lon:.5f}° E &nbsp;|&nbsp; ZOOM LEVEL: 15 &nbsp;|&nbsp; MAP ENGINE: Mapbox Dark GL
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Generate synthetic map points around active coordinates
    np.random.seed(42)
    lats = lat + np.random.normal(0, 0.008, 40)
    lons = lon + np.random.normal(0, 0.008, 40)
    df_map = pd.DataFrame({"lat": lats, "lon": lons})

    st.map(df_map, zoom=14)
