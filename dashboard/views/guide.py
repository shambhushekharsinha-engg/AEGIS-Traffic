"""
AEGIS-Traffic — Learning Guide & Architecture Documentation Page Module (Tab 6)
"""

import streamlit as st

from dashboard.components.widgets import mini_separator, sec_div


def render_guide_page(client):
    """Renders Learning Guide and System Architecture documentation."""
    sec_div("📚 LEARNING GUIDE & MULTIMODAL AI ARCHITECTURE")

    st.markdown(
        """
    <div class="card" style="margin-bottom:16px;">
        <div style="font-family:'Orbitron',sans-serif;color:#00f0ff;font-size:1.1rem;margin-bottom:8px;">
            🚦 AEGIS MULTIMODAL TRAFFIC INTELLIGENCE SYSTEM
        </div>
        <div style="font-family:'JetBrains Mono',monospace;color:#94a3b8;font-size:.78rem;line-height:1.7;">
            AEGIS-Traffic combines edge computer vision, acoustic anomaly detection, zero-shot NLP, automated number plate recognition (ANPR), and relational audit persistence into a zero-trust smart city platform.
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)

    with c1:
        st.markdown(
            """
        <div class="card">
            <div style="font-family:'Orbitron',sans-serif;color:#a855f7;font-size:1.0rem;margin-bottom:8px;">
                👁️ Computer Vision (YOLOv8 & OpenCV)
            </div>
            <div style="font-family:'JetBrains Mono',monospace;color:#64748b;font-size:.75rem;line-height:1.7;">
                • Real-time multi-class vehicle detection (cars, buses, trucks, motorcycles, bicycles).<br>
                • Bounding box tracking & speed estimation via frame-differencing.<br>
                • Optical character recognition (OCR) for ANPR plate reading.<br>
                • Camera tamper & obstruction detection.
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            """
        <div class="card">
            <div style="font-family:'Orbitron',sans-serif;color:#10b981;font-size:1.0rem;margin-bottom:8px;">
                🎙️ Acoustic Anomaly Detection (FFT Spectrograms)
            </div>
            <div style="font-family:'JetBrains Mono',monospace;color:#64748b;font-size:.75rem;line-height:1.7;">
                • Fast Fourier Transform (FFT) spectral frequency analysis.<br>
                • Siren detection (ambulances, fire engines, police vehicles).<br>
                • Crash impact acoustic signature matching.<br>
                • Decibel threshold alert triggers.
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    mini_separator()

    st.markdown(
        '<div class="t-section" style="margin-bottom:8px;">Zero-Trust Security & RBAC Clearances</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
    <div style="font-family:'JetBrains Mono',monospace;font-size:.78rem;color:#94a3b8;line-height:1.8;background:rgba(6,12,26,.8);border:1px solid rgba(0,240,255,.15);border-radius:10px;padding:16px;">
        🔑 <strong>Admin Clearance</strong>: Full system control, lockdown engagement, audit purge.<br>
        👷 <strong>Operator Clearance</strong>: Signal phase overrides, manual timing controls, incident response.<br>
        🔍 <strong>Auditor Clearance</strong>: Read-only access to violation ledgers, export metrics, system logs.
    </div>
    """,
        unsafe_allow_html=True,
    )
