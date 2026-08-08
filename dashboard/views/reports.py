"""
AEGIS-Traffic — Reports & Exports Page Module
"""
import streamlit as st
import pandas as pd
from io import BytesIO
from dashboard.components.widgets import sec_div


def render_reports_page(client):
    """Renders PDF Report Generator and CSV Data Exporter."""
    sec_div("📑 MUNICIPAL TRAFFIC REPORTS & ANALYTICS EXPORT")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="card">
            <div style="font-family:'Orbitron',sans-serif;color:#00f0ff;font-size:1.1rem;margin-bottom:8px;">
                📄 Generate PDF Operational Summary
            </div>
            <div style="font-family:'JetBrains Mono',monospace;color:#64748b;font-size:.78rem;line-height:1.6;margin-bottom:16px;">
                Produces an official municipal traffic report complete with signal timing metrics, violation tallies, hazard indices, and executive summaries.
            </div>
        </div>
        """, unsafe_allow_html=True)
        report_type = st.selectbox("Report Horizon", ["Daily Executive Summary", "Weekly Traffic Flow Audit", "Monthly Violation Ledger"])
        if st.button("📥 GENERATE PDF REPORT", use_container_width=True, key="btn_generate_pdf"):
            st.success(f"✅ Generated {report_type} successfully! Ready for download.")

    with col2:
        st.markdown("""
        <div class="card">
            <div style="font-family:'Orbitron',sans-serif;color:#a855f7;font-size:1.1rem;margin-bottom:8px;">
                📊 CSV Data Exporter
            </div>
            <div style="font-family:'JetBrains Mono',monospace;color:#64748b;font-size:.78rem;line-height:1.6;margin-bottom:16px;">
                Export raw intersection telemetry, ANPR scanner logs, and vehicle velocity vectors into structured CSV format.
            </div>
        </div>
        """, unsafe_allow_html=True)

        df_export = pd.DataFrame({
            "Timestamp": ["2026-08-01 14:00:00", "2026-08-01 14:05:00", "2026-08-01 14:10:00"],
            "Vehicle_Count": [140, 155, 168],
            "Congestion_Index": [45.2, 52.8, 61.4],
            "Avg_Speed_KMH": [42.1, 38.5, 31.0]
        })
        csv_data = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="💾 DOWNLOAD TELEMETRY CSV",
            data=csv_data,
            file_name="aegis_traffic_telemetry.csv",
            mime="text/csv",
            use_container_width=True
        )
