"""
AEGIS-Traffic — GIS Map Intelligence Page Module (Multi-View & 3D Location Controls)
"""

import os
import requests
import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
from dashboard.components.widgets import sec_div, metric_tile, mini_separator
from dashboard.services.cache import cached_geo_sync

CITY_PRESETS = {
    "🇮🇳 New Delhi (Connaught Place)": {
        "lat": 28.6315,
        "lon": 77.2167,
        "name": "Connaught Place, New Delhi",
    },
    "🇮🇳 Mumbai (Bandra-Kurla)": {
        "lat": 19.0657,
        "lon": 72.8687,
        "name": "Bandra-Kurla Complex, Mumbai",
    },
    "🇮🇳 Bengaluru (MG Road)": {
        "lat": 12.9756,
        "lon": 77.6066,
        "name": "MG Road, Bengaluru",
    },
    "🇺🇸 New York (Times Square)": {
        "lat": 40.7580,
        "lon": -73.9855,
        "name": "Times Square, New York",
    },
    "🇬🇧 London (Piccadilly Circus)": {
        "lat": 51.5100,
        "lon": -0.1340,
        "name": "Piccadilly Circus, London",
    },
    "🇯🇵 Tokyo (Shinjuku)": {"lat": 35.6895, "lon": 139.6917, "name": "Shinjuku, Tokyo"},
    "🇸🇬 Singapore (Marina Bay)": {
        "lat": 1.2868,
        "lon": 103.8545,
        "name": "Marina Bay, Singapore",
    },
    "🇦🇪 Dubai (Sheikh Zayed Rd)": {
        "lat": 25.2048,
        "lon": 55.2708,
        "name": "Sheikh Zayed Road, Dubai",
    },
}


def render_maps_page(client):
    """Renders multi-view GIS map with 3D vehicle markers, heatmaps, and smart city location selector."""
    sec_div("🗺️ GIS MAP INTELLIGENCE & SATELLITE TELEMETRY")

    lat = st.session_state.get("latitude", 28.6315)
    lon = st.session_state.get("longitude", 77.2167)
    loc_name = st.session_state.get("location_name", "Connaught Place, New Delhi")

    # ── 3D LOCATION SELECTOR & GEOLOCATION CONTROL ──
    st.markdown(
        """
    <div class="card" style="margin-bottom:16px;">
        <div style="font-family:'Orbitron',sans-serif;color:#00f0ff;font-size:1.1rem;margin-bottom:8px;">
            🌍 3D SMART CITY LOCATION COMMAND
        </div>
        <div style="font-family:'JetBrains Mono',monospace;color:#64748b;font-size:.78rem;line-height:1.6;margin-bottom:12px;">
            Select a global smart city node preset or search any custom location worldwide to re-target the GIS satellite grid and update local currency, speed limits, and traffic laws.
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    c_preset, c_search = st.columns([1.5, 1])

    with c_preset:
        st.markdown(
            '<div class="t-section" style="font-size:.75rem;margin-bottom:6px;">Smart City Presets</div>',
            unsafe_allow_html=True,
        )
        selected_preset = st.selectbox(
            "Select Smart City Preset",
            list(CITY_PRESETS.keys()),
            key="map_preset_selectbox",
            label_visibility="collapsed",
        )
        if st.button(
            "📍 TARGET CITY PRESET", use_container_width=True, key="btn_target_preset"
        ):
            preset_data = CITY_PRESETS[selected_preset]
            st.session_state.latitude = preset_data["lat"]
            st.session_state.longitude = preset_data["lon"]
            st.session_state.location_name = preset_data["name"]

            geo_info = cached_geo_sync(
                st.session_state.location_name,
                st.session_state.latitude,
                st.session_state.longitude,
            )
            for k, v in geo_info.items():
                st.session_state[k] = v
            st.toast(f"📍 Target set to {st.session_state.location_name}", icon="🌍")
            st.rerun()

    with c_search:
        st.markdown(
            '<div class="t-section" style="font-size:.75rem;margin-bottom:6px;">Custom Location Geocoder</div>',
            unsafe_allow_html=True,
        )
        custom_loc = st.text_input(
            "Custom Search Query",
            value="",
            placeholder="e.g. Berlin, Germany",
            label_visibility="collapsed",
            key="map_custom_search_input",
        )
        if st.button(
            "📡 SEARCH GLOBAL NODE",
            use_container_width=True,
            key="btn_search_custom_loc",
        ):
            if custom_loc:
                with st.spinner(f"Geolocating '{custom_loc}'..."):
                    try:
                        osm = requests.get(
                            f"https://nominatim.openstreetmap.org/search?q={requests.utils.quote(custom_loc)}&format=json&limit=1",
                            headers={"User-Agent": "AegisGIS/8.0"},
                            timeout=5,
                        )
                        if osm.ok and osm.json():
                            d = osm.json()[0]
                            st.session_state.latitude = float(d["lat"])
                            st.session_state.longitude = float(d["lon"])
                            parts = d.get("display_name", custom_loc).split(",")
                            st.session_state.location_name = ", ".join(
                                parts[:2]
                            ).strip()

                            geo_info = cached_geo_sync(
                                st.session_state.location_name,
                                st.session_state.latitude,
                                st.session_state.longitude,
                            )
                            for k, v in geo_info.items():
                                st.session_state[k] = v
                            st.toast(
                                f"📍 Located {st.session_state.location_name}",
                                icon="🗺️",
                            )
                            st.rerun()
                        else:
                            st.warning("Location not found — try another city name.")
                    except Exception:
                        st.warning("Geocoder offline — using manual inputs.")

    mini_separator()

    # ── MAP VIEW OPTIONS & CONTROL PANEL ──
    st.markdown(
        '<div class="t-section" style="margin-bottom:10px;">🗺️ MAP VIEW OPTIONS & SATELLITE LAYERS</div>',
        unsafe_allow_html=True,
    )

    mc1, mc2, mc3 = st.columns([1.2, 1, 1])

    with mc1:
        map_view_mode = st.selectbox(
            "MAP VIEW MODE",
            [
                "🛸 3D PyDeck Animated Vehicle Markers",
                "🔥 Real-Time Congestion Heatmap",
                "🏙️ 3D Building & Density Extrusion Columns",
                "🚨 Hazard & Emergency Incident Zones",
                "🗺️ Standard OpenStreetMap Grid",
            ],
            key="map_view_mode_select",
        )

    with mc2:
        zoom_level = st.slider("Map Zoom Level", 10, 18, 14, key="map_zoom_slider")

    with mc3:
        vehicle_filter = st.multiselect(
            "Filter Vehicle Types",
            ["Cars", "Buses", "Trucks", "Motorcycles", "Emergency Vehicles"],
            default=["Cars", "Buses", "Trucks", "Motorcycles"],
            key="map_vehicle_filter_multiselect",
        )

    # ── SYNTHETIC TELEMETRY GENERATION ──
    np.random.seed(42)
    num_points = 60
    lats = lat + np.random.normal(0, 0.006, num_points)
    lons = lon + np.random.normal(0, 0.006, num_points)
    speeds = np.random.randint(10, 75, num_points)
    elevations = np.random.randint(20, 250, num_points)
    v_types = np.random.choice(["Cars", "Buses", "Trucks", "Motorcycles"], num_points)

    df_vehicles = pd.DataFrame(
        {
            "lat": lats,
            "lon": lons,
            "speed": speeds,
            "elevation": elevations,
            "vehicle_type": v_types,
            "color_r": [
                0 if t == "Cars" else (255 if t == "Trucks" else 168) for t in v_types
            ],
            "color_g": [
                240 if t == "Cars" else (68 if t == "Trucks" else 85) for t in v_types
            ],
            "color_b": [
                255 if t == "Cars" else (68 if t == "Trucks" else 247) for t in v_types
            ],
        }
    )

    if vehicle_filter:
        df_vehicles = df_vehicles[df_vehicles["vehicle_type"].isin(vehicle_filter)]

    # Render Active Map Layer based on View Mode
    if "3D PyDeck" in map_view_mode:
        layer = pdk.Layer(
            "ScatterplotLayer",
            df_vehicles,
            get_position=["lon", "lat"],
            get_color=["color_r", "color_g", "color_b", 200],
            get_radius=35,
            pickable=True,
        )
        view_state = pdk.ViewState(
            latitude=lat, longitude=lon, zoom=zoom_level, pitch=45, bearing=30
        )
        r = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={"text": "Type: {vehicle_type}\nSpeed: {speed} km/h"},
        )
        st.pydeck_chart(r)

    elif "Congestion Heatmap" in map_view_mode:
        layer = pdk.Layer(
            "HeatmapLayer",
            df_vehicles,
            get_position=["lon", "lat"],
            get_weight="speed",
            radiusPixels=60,
        )
        view_state = pdk.ViewState(
            latitude=lat, longitude=lon, zoom=zoom_level, pitch=0, bearing=0
        )
        r = pdk.Deck(layers=[layer], initial_view_state=view_state)
        st.pydeck_chart(r)

    elif "3D Building" in map_view_mode:
        layer = pdk.Layer(
            "ColumnLayer",
            df_vehicles,
            get_position=["lon", "lat"],
            get_elevation="elevation",
            elevation_scale=3,
            radius=25,
            get_fill_color=["color_r", "color_g", "color_b", 220],
            pickable=True,
        )
        view_state = pdk.ViewState(
            latitude=lat, longitude=lon, zoom=zoom_level, pitch=60, bearing=-20
        )
        r = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={"text": "Node Density Elevation: {elevation}m"},
        )
        st.pydeck_chart(r)

    elif "Hazard" in map_view_mode:
        df_incidents = df_vehicles.head(10).copy()
        df_incidents["color_r"] = 239
        df_incidents["color_g"] = 68
        df_incidents["color_b"] = 68
        layer = pdk.Layer(
            "ScatterplotLayer",
            df_incidents,
            get_position=["lon", "lat"],
            get_color=[239, 68, 68, 240],
            get_radius=80,
            pickable=True,
        )
        view_state = pdk.ViewState(
            latitude=lat, longitude=lon, zoom=zoom_level, pitch=30, bearing=0
        )
        r = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={"text": "🚨 Hazard Alert: High Congestion / Incident"},
        )
        st.pydeck_chart(r)

    else:
        st.map(df_vehicles[["lat", "lon"]], zoom=zoom_level)

    # ── LIVE GIS TELEMETRY SUMMARY CARDS ──
    mini_separator()
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(
        metric_tile("Active GIS Node", loc_name[:18] + "...", "", "#00f0ff", "📍"),
        unsafe_allow_html=True,
    )
    c2.markdown(
        metric_tile("Active Markers", len(df_vehicles), " units", "#a855f7", "🚗"),
        unsafe_allow_html=True,
    )
    c3.markdown(
        metric_tile("Satellite Sync", "99.8", "%", "#10b981", "🛰️"),
        unsafe_allow_html=True,
    )
    c4.markdown(
        metric_tile("GPS Lat/Lon", f"{lat:.4f}, {lon:.4f}", "", "#eab308", "🌐"),
        unsafe_allow_html=True,
    )
