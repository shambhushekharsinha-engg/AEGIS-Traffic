"""
AEGIS-Traffic — ANPR License Plate Scanner Page Module
"""
import streamlit as st
import pandas as pd
from dashboard.components.widgets import sec_div, metric_tile


def render_anpr_page(client):
    """Renders Automatic Number Plate Recognition (ANPR) detection grid and lookup."""
    sec_div("🚘 AUTOMATIC NUMBER PLATE RECOGNITION (ANPR) SYSTEM")

    token = st.session_state.get("jwt_token", "")
    anpr_data = client.get_anpr(token)

    col1, col2 = st.columns([1.5, 1])

    with col1:
        st.markdown('<div class="t-section" style="margin-bottom:8px;">Live Plate Reader Stream</div>', unsafe_allow_html=True)
        search_query = st.text_input("🔍 Search License Plate Number", placeholder="e.g. DL01-AB-1234", key="anpr_search_input")

        data = [
            {"Timestamp": "14:35:12", "Plate Number": "DL01-AB-1234", "Vehicle Class": "Sedan", "Confidence": "98.4%", "Flag": "CLEAN"},
            {"Timestamp": "14:34:50", "Plate Number": "HR26-CQ-8899", "Vehicle Class": "SUV", "Confidence": "96.1%", "Flag": "STOLEN ALERT"},
            {"Timestamp": "14:34:22", "Plate Number": "UP16-XY-4321", "Vehicle Class": "Motorcycle", "Confidence": "99.0%", "Flag": "CLEAN"},
            {"Timestamp": "14:33:05", "Plate Number": "DL04-CC-9900", "Vehicle Class": "Hatchback", "Confidence": "95.7%", "Flag": "EXPIRED PUC"},
        ]
        df_anpr = pd.DataFrame(data)
        if search_query:
            df_anpr = df_anpr[df_anpr["Plate Number"].str.contains(search_query.upper(), case=False)]
        st.dataframe(df_anpr, use_container_width=True)

    with col2:
        st.markdown('<div class="t-section" style="margin-bottom:8px;">ANPR Detection Metrics</div>', unsafe_allow_html=True)
        st.markdown(metric_tile("Plates Scanned (24h)", "12,450", "", "#00f0ff", "📷"), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(metric_tile("OCR Accuracy", "98.7", "%", "#10b981", "🎯"), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(metric_tile("Hotlist Hits", "14", " matches", "#ef4444", "🚨"), unsafe_allow_html=True)
