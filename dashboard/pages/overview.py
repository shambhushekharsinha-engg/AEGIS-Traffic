"""
AEGIS-Traffic — Command Overview Page Module
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from dashboard.components.widgets import metric_tile, sec_div, risk_color


def render_overview_page(client):
    """Renders the Operations HUD & Command Overview tab."""
    sec_div("📊 TRAFFIC COMMAND HUD — REAL-TIME SENSOR GRID")

    if st.session_state.get("active_data") is None:
        st.markdown("""
        <div class="card" style="text-align:center;padding:60px 20px;">
            <div style="font-size:4rem;margin-bottom:16px;">🚦</div>
            <div class="t-hero" style="font-size:1.4rem;margin-bottom:12px;">SENSOR GRID INITIALIZING</div>
            <div style="font-family:'JetBrains Mono',monospace;color:#4b6584;font-size:.82rem;line-height:1.8;">
                Select a scenario and mode in the left sidebar,<br>then click <strong style="color:#00f0ff;">⚡ EXECUTE SCENARIO SCAN</strong> to boot the HUD.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    data = st.session_state.active_data
    fl = data.get("fusion_layer", {})
    tel = data.get("telemetry", {})
    sm = data.get("system_telemetry_metrics", {})
    alert = fl.get("alert_status", "NORMAL")
    phase = fl.get("active_phase", "North-South Green")
    count = fl.get("vehicle_count", 0)
    timing = fl.get("signal_timing_seconds", 30)
    risk = data.get("risk_score", 15.0)
    lat_ms = data.get("latency_ms", 12)

    # Status Banner
    if any(k in alert for k in ["COLLISION", "EMERGENCY", "LOCKDOWN"]):
        sb_col, sb_bg, sb_border = "#fca5a5", "rgba(239,68,68,.12)", "#ef4444"
    elif any(k in alert for k in ["TAMPER", "WARNING"]):
        sb_col, sb_bg, sb_border = "#fde68a", "rgba(245,158,11,.12)", "#f59e0b"
    else:
        sb_col, sb_bg, sb_border = "#a7f3d0", "rgba(16,185,129,.12)", "#10b981"

    st.markdown(f"""
    <div class="status-banner" style="background:{sb_bg};border-color:{sb_border};color:{sb_col};">
        <span style="font-size:1.3rem;">{"🚨" if sb_border=="#ef4444" else ("⚠️" if sb_border=="#f59e0b" else "✅")}</span>
        <div>
            <div style="font-weight:700;font-size:.9rem;">{alert}</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:.68rem;opacity:.75;margin-top:2px;">
                📍 {st.session_state.get('location_name', 'New Delhi')} &nbsp;|&nbsp; MODE: {st.session_state.get('active_mode', 'AI Automated Fusion')} &nbsp;|&nbsp; PHASE: {phase}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Metric Row
    mc = st.columns(5)
    tiles = [
        ("API Latency", lat_ms, "ms", "#00f0ff", "⏱️"),
        ("Hazard Index", risk, "%", risk_color(risk), "🔥"),
        ("Vehicle Count", count, " units", "#eab308", "🚗"),
        ("Green Timer", f"{timing}s" if timing else "N/A", "", "#a855f7", "🚦"),
        ("System Scans", sm.get("total_requests", 120), " req", "#10b981", "📡"),
    ]
    for col, (lbl, val, unit, clr, ico) in zip(mc, tiles):
        col.markdown(metric_tile(lbl, val, unit, clr, ico), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Main Split
    left, right = st.columns([1.6, 1.4])

    with left:
        sec_div("👁️ LIVE CAMERA FEED — YOLOv8 DETECTION")
        st.markdown(f"""
        <div class="card" style="padding:12px;">
            <div style="background:#000;border-radius:8px;padding:40px;text-align:center;border:1px solid rgba(0,240,255,.2);">
                <div style="font-size:3rem;margin-bottom:10px;">📹</div>
                <div style="font-family:'Orbitron',sans-serif;color:#00f0ff;font-size:1.1rem;">CAMERA NODE #CAM-0412-DELHI</div>
                <div style="font-family:'JetBrains Mono',monospace;color:#64748b;font-size:.75rem;margin-top:4px;">
                    STATUS: ACTIVE STREAM | RESOLUTION: 1080p @ 60FPS | YOLO MULTI-CLASS DETECTOR
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with right:
        sec_div("🚦 SIGNAL PHASE & TIMING CONTROLLER")
        st.markdown(f"""
        <div class="signal-box">
            <div style="font-family:'Orbitron',sans-serif;font-weight:700;color:#e2e8f0;margin-bottom:8px;">
                ACTIVE PHASE: <span style="color:#00f0ff;">{phase}</span>
            </div>
            <div class="signal-dot" style="background:{'#10b981' if 'Green' in phase else '#ef4444'};box-shadow:0 0 20px {'#10b981' if 'Green' in phase else '#ef4444'};"></div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:1.4rem;font-weight:700;color:#00f0ff;">
                {timing}s REMAINING
            </div>
        </div>
        """, unsafe_allow_html=True)
