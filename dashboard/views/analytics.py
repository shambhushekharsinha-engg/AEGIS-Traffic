"""
AEGIS-Traffic — Analytics & Dataset File Analyzer Page Module (Tab 2)
"""

import os
import requests
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dashboard.components.widgets import sec_div, mini_separator, metric_tile

BACKEND = os.environ.get("AEGIS_BACKEND_URL", "http://127.0.0.1:8000")


def render_analytics_page(client):
    """Renders Live Ledger Analytics and Dataset File Analyzer sub-tabs."""
    sec_div("📈 ANALYTICS & DATASET INTELLIGENCE CENTER")

    an_tab_live, an_tab_upload = st.tabs(
        ["📊 Live Ledger Analytics", "📂 Dataset File Analyzer"]
    )

    with an_tab_live:
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown(
                '<div class="t-section" style="margin-bottom:8px;">Traffic Density & Flow Velocity Timeline</div>',
                unsafe_allow_html=True,
            )
            hours = [f"{i:02d}:00" for i in range(24)]
            flow_units = [
                120,
                90,
                45,
                30,
                25,
                40,
                150,
                380,
                520,
                490,
                410,
                430,
                460,
                480,
                510,
                610,
                680,
                640,
                500,
                390,
                290,
                210,
                160,
                130,
            ]
            speed_kmh = [
                55,
                58,
                60,
                62,
                65,
                60,
                45,
                28,
                18,
                22,
                30,
                28,
                26,
                25,
                22,
                15,
                12,
                16,
                25,
                35,
                45,
                50,
                52,
                54,
            ]

            df = pd.DataFrame(
                {
                    "Hour": hours,
                    "Vehicle Flow": flow_units,
                    "Avg Speed (km/h)": speed_kmh,
                }
            )

            fig = px.line(
                df,
                x="Hour",
                y=["Vehicle Flow", "Avg Speed (km/h)"],
                markers=True,
                color_discrete_sequence=["#00f0ff", "#a855f7"],
                title="24-Hour Intersection Volume vs Speed",
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(6,12,26,0.9)",
                font=dict(color="#e2e8f0", family="JetBrains Mono"),
                legend=dict(
                    orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
                ),
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown(
                '<div class="t-section" style="margin-bottom:8px;">Congestion Level Gauge</div>',
                unsafe_allow_html=True,
            )
            gauge = go.Figure(
                go.Indicator(
                    mode="gauge+number",
                    value=68.5,
                    title={
                        "text": "Congestion Index (%)",
                        "font": {"size": 14, "color": "#e2e8f0"},
                    },
                    gauge={
                        "axis": {
                            "range": [None, 100],
                            "tickwidth": 1,
                            "tickcolor": "#4b6584",
                        },
                        "bar": {"color": "#00f0ff"},
                        "bgcolor": "rgba(6,12,26,0.9)",
                        "borderwidth": 2,
                        "bordercolor": "rgba(0,240,255,0.2)",
                        "steps": [
                            {"range": [0, 40], "color": "rgba(16,185,129,0.3)"},
                            {"range": [40, 75], "color": "rgba(245,158,11,0.3)"},
                            {"range": [75, 100], "color": "rgba(239,68,68,0.3)"},
                        ],
                    },
                )
            )
            gauge.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e2e8f0", family="JetBrains Mono"),
            )
            st.plotly_chart(gauge, use_container_width=True)

    with an_tab_upload:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            """
        <div class="card">
            <div style="font-family:'Orbitron',sans-serif;color:#00f0ff;font-size:1.1rem;margin-bottom:8px;">
                📂 TRAFFIC & ANPR DATASET FILE ANALYZER
            </div>
            <div style="font-family:'JetBrains Mono',monospace;color:#64748b;font-size:.78rem;line-height:1.6;">
                Upload raw CSV or JSON dataset files for instant exploratory data analysis (EDA), anomaly profiling, and distribution summary.
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Choose a traffic dataset file (CSV or JSON)",
            type=["csv", "json"],
            key="dataset_analyzer_uploader",
        )
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".csv"):
                    df_up = pd.read_csv(uploaded_file)
                else:
                    df_up = pd.read_json(uploaded_file)

                st.success(
                    f"✅ Successfully loaded '{uploaded_file.name}' — {len(df_up)} rows, {len(df_up.columns)} columns."
                )

                c1, c2, c3 = st.columns(3)
                c1.markdown(
                    metric_tile("Total Records", len(df_up), " rows", "#00f0ff", "📊"),
                    unsafe_allow_html=True,
                )
                c2.markdown(
                    metric_tile(
                        "Total Fields", len(df_up.columns), " cols", "#a855f7", "📋"
                    ),
                    unsafe_allow_html=True,
                )
                c3.markdown(
                    metric_tile(
                        "Memory Usage",
                        f"{uploaded_file.size / 1024:.1f}",
                        " KB",
                        "#10b981",
                        "💾",
                    ),
                    unsafe_allow_html=True,
                )

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(
                    '<div class="t-section" style="margin-bottom:8px;">Dataset Preview</div>',
                    unsafe_allow_html=True,
                )
                st.dataframe(df_up.head(10), use_container_width=True)

                st.markdown(
                    '<div class="t-section" style="margin-top:16px;margin-bottom:8px;">Descriptive Statistics</div>',
                    unsafe_allow_html=True,
                )
                st.dataframe(df_up.describe(include="all"), use_container_width=True)
            except Exception as e:
                st.error(f"❌ Failed to parse dataset file: {e}")
        else:
            st.info("ℹ️ Upload a CSV or JSON file to analyze records.")
