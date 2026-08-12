"""
AEGIS-Traffic — GIS Map Intelligence Page Module (Multi-View & 3D Location Controls)
Enhanced v2: Arc Layer routing, live stats overlay, incident markers, route intelligence.
"""

import random

import numpy as np
import pandas as pd
import pydeck as pdk
import requests
import streamlit as st

from dashboard.components.widgets import metric_tile, mini_separator, sec_div
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


def _make_vehicle_df(lat, lon, seed=42):
    np.random.seed(seed)
    num_points = 80
    lats = lat + np.random.normal(0, 0.007, num_points)
    lons = lon + np.random.normal(0, 0.007, num_points)
    speeds = np.random.randint(5, 85, num_points)
    elevations = np.random.randint(20, 280, num_points)
    v_types = np.random.choice(
        ["Cars", "Buses", "Trucks", "Motorcycles", "Emergency"], num_points
    )

    def _color(t, s):
        if t == "Emergency":
            return [255, 50, 50]
        if s < 20:
            return [239, 68, 68]  # red = slow
        if s < 45:
            return [234, 179, 8]  # yellow = moderate
        return [34, 197, 94]  # green = free flow

    colors = [_color(t, s) for t, s in zip(v_types, speeds)]
    return pd.DataFrame(
        {
            "lat": lats,
            "lon": lons,
            "speed": speeds,
            "elevation": elevations,
            "vehicle_type": v_types,
            "color_r": [c[0] for c in colors],
            "color_g": [c[1] for c in colors],
            "color_b": [c[2] for c in colors],
        }
    )


def _make_arc_df(lat, lon, seed=7):
    """Generate synthetic route arcs for demonstration."""
    random.seed(seed)
    arcs = []
    origins = [
        (lat + random.uniform(-0.012, 0.012), lon + random.uniform(-0.012, 0.012))
        for _ in range(12)
    ]
    destinations = [
        (lat + random.uniform(-0.012, 0.012), lon + random.uniform(-0.012, 0.012))
        for _ in range(12)
    ]
    for (slat, slon), (tlat, tlon) in zip(origins, destinations):
        arcs.append(
            {
                "start_lat": slat,
                "start_lon": slon,
                "end_lat": tlat,
                "end_lon": tlon,
                "volume": random.randint(50, 500),
            }
        )
    return pd.DataFrame(arcs)


def _make_incident_df(lat, lon, seed=13):
    np.random.seed(seed)
    n = 8
    labels = [
        "Congestion",
        "Accident",
        "Roadwork",
        "Flooding",
        "Event",
        "Breakdown",
        "Fire Truck",
        "Signal Fault",
    ]
    return pd.DataFrame(
        {
            "lat": lat + np.random.normal(0, 0.008, n),
            "lon": lon + np.random.normal(0, 0.008, n),
            "label": labels,
            "severity": np.random.choice(["HIGH", "MEDIUM", "LOW"], n),
        }
    )


def _make_route_df(lat, lon, seed=99):
    """Generate synthetic path routes for the original 3D animated route view."""
    np.random.seed(seed)
    n = 20
    paths = []
    for _ in range(n):
        slat = lat + np.random.normal(0, 0.015)
        slon = lon + np.random.normal(0, 0.015)
        path = []
        for i in range(10):
            path.append(
                [
                    slon + (i * np.random.normal(0.001, 0.0005)),
                    slat + (i * np.random.normal(0.001, 0.0005)),
                ]
            )
        paths.append(
            {
                "path": path,
                "color": [
                    np.random.randint(50, 255),
                    np.random.randint(50, 255),
                    255,
                    200,
                ],
            }
        )
    return pd.DataFrame(paths)


def render_maps_page(client):
    """Renders multi-view GIS map with enhanced layers, incident overlay, and route intelligence."""
    sec_div("🗺️ GIS MAP INTELLIGENCE & REAL-TIME TELEMETRY")

    lat = st.session_state.get("latitude", 28.6315)
    lon = st.session_state.get("longitude", 77.2167)
    loc_name = st.session_state.get("location_name", "Connaught Place, New Delhi")

    # ── LOCATION COMMAND BAR ──────────────────────────────────────────────────────
    st.markdown(
        """
    <div class="card" style="margin-bottom:16px;">
        <div style="font-family:'Orbitron',sans-serif;color:#00f0ff;font-size:1.1rem;margin-bottom:8px;">
            🌍 SMART CITY LOCATION COMMAND
        </div>
        <div style="font-family:'JetBrains Mono',monospace;color:#64748b;font-size:.78rem;line-height:1.6;margin-bottom:4px;">
            Select a global smart city node or search any custom location to re-target the GIS satellite grid.
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    c_preset, c_search = st.columns([1.5, 1])

    with c_preset:
        st.markdown(
            '<div class="t-section" style="font-size:.75rem;margin-bottom:6px;">Global Smart City Nodes</div>',
            unsafe_allow_html=True,
        )
        selected_city = st.selectbox(
            "Select City Node",
            list(CITY_PRESETS.keys()),
            key="map_city_preset_select",
            label_visibility="collapsed",
        )
        if st.button(
            "🚀 DEPLOY TO NODE", use_container_width=True, key="btn_deploy_city"
        ):
            preset = CITY_PRESETS[selected_city]
            st.session_state.latitude = preset["lat"]
            st.session_state.longitude = preset["lon"]
            st.session_state.location_name = preset["name"]
            geo_info = cached_geo_sync(preset["name"], preset["lat"], preset["lon"])
            for k, v in geo_info.items():
                st.session_state[k] = v
            st.toast(f"📡 GIS grid deployed to {preset['name']}", icon="🗺️")
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
            "🔍 SEARCH GLOBAL NODE",
            use_container_width=True,
            key="btn_search_custom_loc",
        ):
            if custom_loc:
                with st.spinner(f"Geolocating '{custom_loc}'..."):
                    try:
                        osm = requests.get(
                            f"https://nominatim.openstreetmap.org/search?q={requests.utils.quote(custom_loc)}&format=json&limit=1",
                            headers={"User-Agent": "AegisGIS/9.0"},
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
                                icon="✅",
                            )
                            st.rerun()
                        else:
                            st.warning("Location not found — try another city name.")
                    except Exception:
                        st.warning("Geocoder offline — using manual inputs.")

    mini_separator()

    # ── MAP CONTROLS ──────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="t-section" style="margin-bottom:10px;">📡 MAP VIEW OPTIONS & SATELLITE LAYERS</div>',
        unsafe_allow_html=True,
    )

    mc1, mc2, mc3, mc4 = st.columns([1.4, 0.8, 0.8, 0.8])

    with mc1:
        map_view_mode = st.selectbox(
            "MAP VIEW MODE",
            [
                "🚗 Live Vehicle Markers (Speed-Colour Coded)",
                "🛣️ 3D Animated Vehicle Routes (Original)",
                "🔥 Real-Time Congestion Heatmap",
                "🏙️ 3D Density Extrusion Columns",
                "🌐 Route Arc Intelligence Layer",
                "🚨 Hazard & Incident Zones",
                "🗺️ Standard OpenStreetMap Grid",
            ],
            key="map_view_mode_select",
        )

    with mc2:
        zoom_level = st.slider("Zoom Level", 10, 18, 14, key="map_zoom_slider")

    with mc3:
        pitch_level = st.slider("3D Pitch", 0, 70, 40, step=10, key="map_pitch_slider")

    with mc4:
        map_theme = st.selectbox(
            "Map Theme", ["Dark Mode", "Light Mode"], key="map_theme_select"
        )

    # ── ADVANCED CONTROLS ROW ─────────────────────────────────────────────────────
    adv1, adv2, adv3, adv4 = st.columns([1, 1, 1, 1])

    with adv1:
        show_incidents = st.toggle(
            "🚨 Overlay Incident Markers", value=True, key="map_show_incidents"
        )

    with adv2:
        live_refresh = st.toggle(
            "⚡ Live Position Refresh", value=False, key="map_live_refresh"
        )

    with adv3:
        vehicle_filter = st.multiselect(
            "Filter Vehicles",
            ["Cars", "Buses", "Trucks", "Motorcycles", "Emergency"],
            default=["Cars", "Buses", "Trucks", "Motorcycles", "Emergency"],
            key="map_vehicle_filter_multiselect",
        )

    with adv4:
        # Heatmap time-lapse: only visible when heatmap is selected
        if "Heatmap" in map_view_mode:
            timelapse_hour = st.slider(
                "🕐 Historical Hour (Time-Lapse)",
                min_value=0,
                max_value=23,
                value=12,
                format="%H:00",
                key="map_timelapse_hour",
            )
            st.caption(
                f"Showing simulated congestion snapshot for **{timelapse_hour:02d}:00** — "
                "slide to replay historical traffic density."
            )
        else:
            timelapse_hour = 12  # default seed

    # ── LIVE POSITION REFRESH (WebSocket simulation via st.rerun) ─────────────────
    if live_refresh:
        import time

        st.markdown(
            "<div style=\"font-family:'JetBrains Mono',monospace;color:#10b981;"
            'font-size:.7rem;margin-bottom:4px;">'
            "⚡ LIVE MODE — Position data refreshing every 5s</div>",
            unsafe_allow_html=True,
        )
        refresh_seed = int(time.time()) // 5  # Changes every 5 seconds
    else:
        refresh_seed = 42

    # ── DATA GENERATION ───────────────────────────────────────────────────────────
    # Time-lapse seed: shift congestion pattern based on hour of day
    # Peak hours (8-10, 17-20) = denser, slower. Off-peak = sparse, faster.
    peak_factor = 1.0
    if "Heatmap" in map_view_mode:
        if timelapse_hour in range(8, 11) or timelapse_hour in range(17, 21):
            peak_factor = 2.2  # Rush hour — very congested
        elif timelapse_hour in range(11, 17):
            peak_factor = 1.2  # Midday — moderate
        elif timelapse_hour in range(0, 6):
            peak_factor = 0.3  # Night — sparse
        else:
            peak_factor = 0.8  # Off-peak

    df_vehicles = _make_vehicle_df(lat, lon, seed=refresh_seed)
    # Scale speed inversely with peak factor (more congested = slower)
    df_vehicles["speed"] = np.clip(df_vehicles["speed"] / peak_factor, 5, 85).astype(
        int
    )
    if vehicle_filter:
        df_vehicles = df_vehicles[df_vehicles["vehicle_type"].isin(vehicle_filter)]

    df_incidents = _make_incident_df(lat, lon)
    df_arcs = _make_arc_df(lat, lon)
    df_routes = _make_route_df(lat, lon)

    # ── MAP RENDERING ─────────────────────────────────────────────────────────────
    if map_theme == "Light Mode":
        MAP_STYLE = "mapbox://styles/mapbox/light-v10"
    else:
        MAP_STYLE = "mapbox://styles/mapbox/dark-v10"

    view_state = pdk.ViewState(
        latitude=lat, longitude=lon, zoom=zoom_level, pitch=pitch_level, bearing=0
    )

    incident_layer = pdk.Layer(
        "ScatterplotLayer",
        df_incidents,
        get_position=["lon", "lat"],
        get_color=[255, 50, 50, 220],
        get_radius=70,
        pickable=True,
    )

    if "Live Vehicle" in map_view_mode:
        main_layer = pdk.Layer(
            "ScatterplotLayer",
            df_vehicles,
            get_position=["lon", "lat"],
            get_color=["color_r", "color_g", "color_b", 210],
            get_radius=30,
            pickable=True,
            auto_highlight=True,
        )
        tooltip = {
            "html": "<b>Type:</b> {vehicle_type}<br/><b>Speed:</b> {speed} km/h",
            "style": {
                "backgroundColor": "#0f172a",
                "color": "#00f0ff",
                "fontSize": "12px",
                "padding": "8px",
            },
        }

    elif "Animated Vehicle Routes" in map_view_mode:
        main_layer = pdk.Layer(
            "PathLayer",
            df_routes,
            get_path="path",
            get_color="color",
            width_scale=20,
            width_min_pixels=2,
            get_width=5,
            pickable=True,
            auto_highlight=True,
        )
        tooltip = {
            "html": "<b>Live Route Track</b>",
            "style": {
                "backgroundColor": "#0f172a",
                "color": "#00f0ff",
                "fontSize": "12px",
                "padding": "8px",
            },
        }

    elif "Congestion Heatmap" in map_view_mode:
        # Invert speed to weight: slow = high weight = hot
        df_vehicles["heat_weight"] = 90 - df_vehicles["speed"]
        main_layer = pdk.Layer(
            "HeatmapLayer",
            df_vehicles,
            get_position=["lon", "lat"],
            get_weight="heat_weight",
            radiusPixels=70,
            intensity=1.0,
            threshold=0.05,
        )
        tooltip = None

    elif "3D Density" in map_view_mode:
        main_layer = pdk.Layer(
            "ColumnLayer",
            df_vehicles,
            get_position=["lon", "lat"],
            get_elevation="elevation",
            elevation_scale=4,
            radius=28,
            get_fill_color=["color_r", "color_g", "color_b", 220],
            pickable=True,
            auto_highlight=True,
        )
        tooltip = {
            "html": "<b>Node Density:</b> {elevation}m<br/><b>Type:</b> {vehicle_type}",
            "style": {
                "backgroundColor": "#0f172a",
                "color": "#a855f7",
                "fontSize": "12px",
            },
        }

    elif "Route Arc" in map_view_mode:
        main_layer = pdk.Layer(
            "ArcLayer",
            df_arcs,
            get_source_position=["start_lon", "start_lat"],
            get_target_position=["end_lon", "end_lat"],
            get_source_color=[0, 240, 255, 200],
            get_target_color=[168, 85, 247, 200],
            get_width="volume / 80",
            pickable=True,
            auto_highlight=True,
        )
        tooltip = {
            "html": "<b>Route Volume:</b> {volume} vehicles/hr",
            "style": {
                "backgroundColor": "#0f172a",
                "color": "#00f0ff",
                "fontSize": "12px",
            },
        }

    elif "Hazard" in map_view_mode:
        df_high = df_incidents.copy()
        main_layer = pdk.Layer(
            "ScatterplotLayer",
            df_high,
            get_position=["lon", "lat"],
            get_color=[239, 68, 68, 240],
            get_radius=90,
            pickable=True,
            auto_highlight=True,
        )
        tooltip = {
            "html": "<b>🚨 {label}</b><br/>Severity: {severity}",
            "style": {
                "backgroundColor": "#1a0000",
                "color": "#ff4444",
                "fontSize": "12px",
            },
        }

    else:
        st.map(df_vehicles[["lat", "lon"]], zoom=zoom_level)
        mini_separator()

    if "Standard" not in map_view_mode:
        layers = [main_layer]
        if show_incidents and "Hazard" not in map_view_mode:
            layers.append(incident_layer)

        deck = pdk.Deck(
            layers=layers,
            initial_view_state=view_state,
            map_style=MAP_STYLE,
            tooltip=tooltip,
        )
        st.pydeck_chart(deck, use_container_width=True)

    # ── COLOUR LEGEND ─────────────────────────────────────────────────────────────
    if "Live Vehicle" in map_view_mode:
        st.markdown(
            """
        <div style="display:flex;gap:18px;padding:8px 0;font-family:'JetBrains Mono',monospace;font-size:.72rem;">
            <span style="color:#22c55e;">■ Free Flow (&gt;45 km/h)</span>
            <span style="color:#eab308;">■ Moderate (20–45 km/h)</span>
            <span style="color:#ef4444;">■ Congested (&lt;20 km/h)</span>
            <span style="color:#ff3232;">■ Emergency Vehicle</span>
        </div>
        """,
            unsafe_allow_html=True,
        )

    if "Route Arc" in map_view_mode:
        st.markdown(
            """
        <div style="display:flex;gap:18px;padding:8px 0;font-family:'JetBrains Mono',monospace;font-size:.72rem;">
            <span style="color:#00f0ff;">■ Origin Node</span>
            <span style="color:#a855f7;">■ Destination Node</span>
            <span>Arc width = relative traffic volume</span>
        </div>
        """,
            unsafe_allow_html=True,
        )

    mini_separator()

    # ── INCIDENT SUMMARY TABLE ─────────────────────────────────────────────────────
    with st.expander("🚨 Active Incident Feed", expanded=False):
        severity_color = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
        df_incidents["Status"] = (
            df_incidents["severity"].map(severity_color)
            + " "
            + df_incidents["severity"]
        )
        st.dataframe(
            df_incidents[["label", "Status", "lat", "lon"]].rename(
                columns={
                    "label": "Incident Type",
                    "lat": "Latitude",
                    "lon": "Longitude",
                }
            ),
            use_container_width=True,
        )

    # ── LIVE GIS TELEMETRY SUMMARY CARDS ──────────────────────────────────────────
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
        metric_tile("GPS Lat/Lon", f"{lat:.4f}, {lon:.4f}", "", "#eab308", "🌍"),
        unsafe_allow_html=True,
    )
