"""
AEGIS-Traffic — Predictive Analytics Page Module
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dashboard.components.widgets import sec_div


def render_analytics_page(client):
    """Renders traffic volume timeline, congestion index, and historical metrics."""
    sec_div("📈 PREDICTIVE ANALYTICS & CONGESTION FORECASTING")

    token = st.session_state.get("jwt_token", "")
    history_data = client.get_history(token)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown('<div class="t-section" style="margin-bottom:8px;">Traffic Density & Flow Velocity Timeline</div>', unsafe_allow_html=True)
        # Generate sample timeseries
        hours = [f"{i:02d}:00" for i in range(24)]
        flow_units = [120, 90, 45, 30, 25, 40, 150, 380, 520, 490, 410, 430, 460, 480, 510, 610, 680, 640, 500, 390, 290, 210, 160, 130]
        speed_kmh = [55, 58, 60, 62, 65, 60, 45, 28, 18, 22, 30, 28, 26, 25, 22, 15, 12, 16, 25, 35, 45, 50, 52, 54]

        df = pd.DataFrame({"Hour": hours, "Vehicle Flow": flow_units, "Avg Speed (km/h)": speed_kmh})

        fig = px.line(df, x="Hour", y=["Vehicle Flow", "Avg Speed (km/h)"], markers=True,
                      color_discrete_sequence=["#00f0ff", "#a855f7"],
                      title="24-Hour Intersection Volume vs Speed")
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(6,12,26,0.9)",
            font=dict(color="#e2e8f0", family="JetBrains Mono"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="t-section" style="margin-bottom:8px;">Congestion Level Gauge</div>', unsafe_allow_html=True)
        gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=68.5,
            title={'text': "Congestion Index (%)", 'font': {'size': 14, 'color': "#e2e8f0"}},
            gauge={
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#4b6584"},
                'bar': {'color': "#00f0ff"},
                'bgcolor': "rgba(6,12,26,0.9)",
                'borderwidth': 2,
                'bordercolor': "rgba(0,240,255,0.2)",
                'steps': [
                    {'range': [0, 40], 'color': 'rgba(16,185,129,0.3)'},
                    {'range': [40, 75], 'color': 'rgba(245,158,11,0.3)'},
                    {'range': [75, 100], 'color': 'rgba(239,68,68,0.3)'}
                ],
            }
        ))
        gauge.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#e2e8f0", family="JetBrains Mono"))
        st.plotly_chart(gauge, use_container_width=True)
