"""
AEGIS-Traffic — Traffic Violation Logs Page Module
"""

import pandas as pd
import streamlit as st

from dashboard.components.widgets import metric_tile, sec_div


def render_violations_page(client):
    """Renders automated violation detection grid, fine summaries, and evidence viewer."""
    sec_div("🚨 AUTOMATED TRAFFIC VIOLATION AUDIT LEDGER")

    token = st.session_state.get("jwt_token", "")
    client.get_violations(token)

    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(
        metric_tile("Total Violations", "148", " cases", "#ef4444", "📜"),
        unsafe_allow_html=True,
    )
    col2.markdown(
        metric_tile("Speeding Violations", "84", " cases", "#f59e0b", "⚡"),
        unsafe_allow_html=True,
    )
    col3.markdown(
        metric_tile("Red Light Jumps", "42", " cases", "#ef4444", "🚦"),
        unsafe_allow_html=True,
    )
    col4.markdown(
        metric_tile("Fines Issued", "₹2,14,000", "", "#10b981", "💰"),
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div class="t-section" style="margin-bottom:8px;">Recent Violation Records</div>',
        unsafe_allow_html=True,
    )

    # Sample table data
    data = [
        {
            "Case ID": "VIO-9041",
            "Vehicle Plate": "DL01-AB-1234",
            "Violation Type": "SPEEDING (78 km/h)",
            "Fine Amount": "₹2,000",
            "Timestamp": "14:32:10 UTC",
            "Status": "ISSUED",
        },
        {
            "Case ID": "VIO-9042",
            "Vehicle Plate": "HR26-CQ-8899",
            "Violation Type": "RED LIGHT CROSSING",
            "Fine Amount": "₹5,000",
            "Timestamp": "14:28:45 UTC",
            "Status": "PAID",
        },
        {
            "Case ID": "VIO-9043",
            "Vehicle Plate": "UP16-XY-4321",
            "Violation Type": "NO HELMET",
            "Fine Amount": "₹1,000",
            "Timestamp": "14:15:02 UTC",
            "Status": "PENDING",
        },
        {
            "Case ID": "VIO-9044",
            "Vehicle Plate": "DL04-CC-9900",
            "Violation Type": "TRIPLE RIDING",
            "Fine Amount": "₹1,000",
            "Timestamp": "13:58:20 UTC",
            "Status": "ISSUED",
        },
    ]
    df_vio = pd.DataFrame(data)
    st.dataframe(df_vio, use_container_width=True)
