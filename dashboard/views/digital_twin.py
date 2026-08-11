"""
AEGIS-Traffic — 3D Digital Twin Visualization (v9.0.0)
"""

import random

import pandas as pd
import pydeck as pdk
import streamlit as st

from dashboard.components.widgets import sec_div


def render_digital_twin_page(client):
    """Renders the interactive 3D Digital Twin using deck.gl."""
    sec_div("🏙️ 3D DIGITAL TWIN & SPATIAL TRACKING")

    st.markdown(
        """
    <div class="t-sub" style="margin-bottom:16px;">
        REAL-TIME SPATIAL RECONSTRUCTION // CONNECTED V2X VEHICLES & EDGE NODES
    </div>
    """,
        unsafe_allow_html=True,
    )

    lat = st.session_state.get("latitude", 28.6315)
    lon = st.session_state.get("longitude", 77.2167)

    # Generate some random 3D "vehicle" trajectories near the center
    num_vehicles = 50
    data = []
    for _ in range(num_vehicles):
        data.append(
            {
                "lat": lat + random.uniform(-0.015, 0.015),
                "lon": lon + random.uniform(-0.015, 0.015),
                "elevation": random.randint(10, 50),
                "color": (
                    [random.randint(0, 255), 240, 255, 200]
                    if random.random() > 0.2
                    else [255, 0, 80, 200]
                ),  # Cyan/Blue or Red for emergency
                "speed": random.randint(20, 80),
            }
        )
    df = pd.DataFrame(data)

    # PyDeck Map
    view_state = pdk.ViewState(
        latitude=lat, longitude=lon, zoom=14.5, pitch=60, bearing=-20
    )

    # Hexagon layer to simulate density
    hex_layer = pdk.Layer(
        "HexagonLayer",
        data=df,
        get_position=["lon", "lat"],
        radius=100,
        elevation_scale=4,
        elevation_range=[0, 1000],
        extruded=True,
        get_fill_color=[0, 240, 255, 120],
    )

    # Scatterplot layer for vehicles
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=["lon", "lat"],
        get_color="color",
        get_radius="elevation * 2",
        pickable=True,
    )

    r = pdk.Deck(
        layers=[hex_layer, scatter_layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/dark-v10",
        tooltip={"text": "Speed: {speed} km/h"},
    )

    # Custom CSS for the map container to make it look cyber
    st.markdown(
        """
    <style>
    #deckgl-wrapper {
        border: 1px solid #00f0ff;
        border-radius: 8px;
        box-shadow: 0 0 20px rgba(0, 240, 255, 0.1);
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    st.pydeck_chart(r)

    # Status Panel
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label="Active V2X Nodes", value=f"{random.randint(800, 1500)}", delta="+12"
        )
    with col2:
        st.metric(label="ReID Match Rate", value="94.2%", delta="0.5%")
    with col3:
        st.metric(
            label="Federated Syncs",
            value=f"{random.randint(40, 90)}/hr",
            delta="Active",
            delta_color="normal",
        )
