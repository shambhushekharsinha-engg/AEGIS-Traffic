"""
AEGIS-Traffic — Operations HUD Page Module (Tab 1)
"""

import os

import requests
import streamlit as st

from dashboard.components.widgets import (
    metric_tile,
    mini_separator,
    risk_color,
    sec_div,
)

BACKEND = os.environ.get("AEGIS_BACKEND_URL", "http://127.0.0.1:8000")


def render_overview_page(client):
    """Renders the complete Operations HUD tab."""
    if st.session_state.get("active_data") is None:
        st.markdown(
            """
        <div class="card" style="text-align:center;padding:60px 20px;">
            <div style="font-size:4rem;margin-bottom:16px;">🚦</div>
            <div class="t-hero" style="font-size:1.4rem;margin-bottom:12px;">SENSOR GRID OFFLINE</div>
            <div style="font-family:'JetBrains Mono',monospace;color:#4b6584;font-size:.82rem;line-height:1.8;">
                Select a scenario and mode in the left sidebar,<br>then click <strong style="color:#00f0ff;">⚡ EXECUTE SCENARIO SCAN</strong> to boot the HUD.
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )
        return

    data = st.session_state.active_data
    fl = data.get("fusion_layer", {})
    data.get("telemetry", {})
    sm = data.get("system_telemetry_metrics", {})
    alert = fl.get("alert_status", "NORMAL")
    phase = fl.get("active_phase", "North-South Green")
    count = fl.get("vehicle_count", 0)
    timing = fl.get("signal_timing_seconds", 30)
    risk = data.get("risk_score", 15.0)
    lat_ms = data.get("latency_ms", 12)

    # ── STATUS BANNER
    if any(k in alert for k in ["COLLISION", "EMERGENCY", "LOCKDOWN"]):
        sb_col, sb_bg, sb_border = "#fca5a5", "rgba(239,68,68,.12)", "#ef4444"
    elif any(k in alert for k in ["TAMPER", "WARNING"]):
        sb_col, sb_bg, sb_border = "#fde68a", "rgba(245,158,11,.12)", "#f59e0b"
    elif "MANUAL" in alert:
        sb_col, sb_bg, sb_border = "#c4b5fd", "rgba(168,85,247,.12)", "#a855f7"
    elif "PREDICTIVE" in alert:
        sb_col, sb_bg, sb_border = "#bae6fd", "rgba(6,182,212,.12)", "#06b6d4"
    else:
        sb_col, sb_bg, sb_border = "#a7f3d0", "rgba(16,185,129,.12)", "#10b981"

    st.markdown(
        f"""
    <div class="status-banner" style="background:{sb_bg};border-color:{sb_border};color:{sb_col};">
        <span style="font-size:1.3rem;">{"🚨" if sb_border == "#ef4444" else ("⚠️" if sb_border == "#f59e0b" else "✅")}</span>
        <div>
            <div style="font-weight:700;font-size:.9rem;">{alert}</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:.68rem;opacity:.75;margin-top:2px;">
                📍 {st.session_state.get('location_name', 'New Delhi')} &nbsp;|&nbsp; MODE: {st.session_state.get('active_mode', 'AI Automated Fusion')} &nbsp;|&nbsp; PHASE: {phase}
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # ── METRIC ROW
    mc = st.columns(5)
    tiles = [
        ("API Latency", lat_ms, "ms", "#00f0ff", "⏱️"),
        ("Hazard Index", risk, "%", risk_color(risk), "🔥"),
        ("Vehicle Count", count, " units", "#eab308", "🚗"),
        ("Green Timer", f"{timing}s" if timing else "N/A", "", "#a855f7", "🚦"),
        ("System Scans", sm.get("total_requests", 0), " req", "#10b981", "📡"),
    ]
    for col, (lbl, val, unit, clr, ico) in zip(mc, tiles):
        col.markdown(metric_tile(lbl, val, unit, clr, ico), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── MAIN SPLIT
    left, right = st.columns([1.6, 1.4])

    with left:
        sec_div("👁️ LIVE CAMERA FEED — YOLOv8 DETECTION")
        st.markdown(
            f"""
        <div class="card" style="padding:12px;">
            <div style="background:#000;border-radius:8px;padding:40px;text-align:center;border:1px solid rgba(0,240,255,.2);">
                <div style="font-size:3rem;margin-bottom:10px;">📹</div>
                <div style="font-family:'Orbitron',sans-serif;color:#00f0ff;font-size:1.1rem;">CAMERA NODE #CAM-0412-DELHI</div>
                <div style="font-family:'JetBrains Mono',monospace;color:#64748b;font-size:.75rem;margin-top:4px;">
                    STATUS: ACTIVE STREAM | RESOLUTION: 1080p @ 60FPS | YOLO MULTI-CLASS DETECTOR
                </div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with right:
        sec_div("🚦 SIGNAL PHASE & TIMING CONTROLLER")
        st.markdown(
            f"""
        <div class="signal-box">
            <div style="font-family:'Orbitron',sans-serif;font-weight:700;color:#e2e8f0;margin-bottom:8px;">
                ACTIVE PHASE: <span style="color:#00f0ff;">{phase}</span>
            </div>
            <div class="signal-dot" style="background:{'#10b981' if 'Green' in phase else '#ef4444'};box-shadow:0 0 20px {'#10b981' if 'Green' in phase else '#ef4444'};"></div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:1.4rem;font-weight:700;color:#00f0ff;">
                {timing}s REMAINING
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # ── TRAFFIC ANALYTICS
    mini_separator()
    sec_div("📊 TRAFFIC ANALYTICS — DENSITY · QUEUE · SPEED · LANES")
    ta = data.get("traffic_analytics", {})
    if ta:
        ta1, ta2, ta3, ta4 = st.columns(4)
        ta1.markdown(
            metric_tile(
                "Traffic Density",
                ta.get("traffic_density_percent", "—"),
                "%",
                "#00f0ff",
                "📊",
            ),
            unsafe_allow_html=True,
        )
        ta2.markdown(
            metric_tile(
                "Queue Length", ta.get("queue_length_meters", "—"), "m", "#a855f7", "📏"
            ),
            unsafe_allow_html=True,
        )
        ta3.markdown(
            metric_tile(
                "Avg Speed", ta.get("avg_speed_kmh", "—"), "km/h", "#10b981", "⚡"
            ),
            unsafe_allow_html=True,
        )
        ta4.markdown(
            metric_tile(
                "Density Level", ta.get("density_level", "—"), "", "#eab308", "🏷️"
            ),
            unsafe_allow_html=True,
        )

        lc = ta.get("lane_counts", {})
        if lc:
            st.markdown("<br>", unsafe_allow_html=True)
            lc_cols = st.columns(len(lc))
            for col, (lane, cnt) in zip(lc_cols, lc.items()):
                col.markdown(
                    metric_tile(lane, cnt, " veh", "#06b6d4", "🛣️"),
                    unsafe_allow_html=True,
                )

    # ── ENVIRONMENTAL EXHAUST & VRU PEDESTRIAN SAFETY
    mini_separator()
    sec_div("🌱 ENVIRONMENTAL EXHAUST TELEMETRY · 🚶 VRU PEDESTRIAN SAFETY")
    env_col, vru_col = st.columns(2)
    with env_col:
        try:
            _env_res = requests.get(
                f"{BACKEND}/api/v1/environmental/telemetry",
                params={"vehicle_count": count, "signal_timing_seconds": timing or 30},
                timeout=5,
            )
            if _env_res.ok:
                _env = _env_res.json()
                st.markdown(
                    f"""
                <div class="card" style="border-color:rgba(16,185,129,.2);">
                    <div style="font-family:'Orbitron',sans-serif;font-size:.78rem;font-weight:700;color:#10b981;margin-bottom:8px;">
                        🍃 IDLE EXHAUST EMISSIONS
                    </div>
                    <div style="font-family:'JetBrains Mono',monospace;font-size:.72rem;line-height:1.9;">
                        CO₂ Output: <strong style="color:#00f0ff;">{_env['co2_grams']} g</strong> &nbsp;|&nbsp;
                        NOx: <strong style="color:#a855f7;">{_env['nox_grams']} g</strong><br>
                        PM2.5 Rate: <strong style="color:#f59e0b;">{_env['pm25_grams']} g</strong> &nbsp;|&nbsp;
                        ATSC Saved: <strong style="color:#10b981;">{_env['atsc_carbon_saved_grams']} g CO₂</strong><br>
                        LEZ Status: <strong style="color:{'#10b981' if 'COMPLIANT' in _env['lez_status'] else '#ef4444'};">{_env['lez_status']}</strong>
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )
        except Exception:
            st.warning("Environmental module offline.")
    with vru_col:
        try:
            _vru_res = requests.get(
                f"{BACKEND}/api/v1/vru/crosswalk", params={"pedestrians": 3}, timeout=5
            )
            if _vru_res.ok:
                _vru = _vru_res.json()
                st.markdown(
                    f"""
                <div class="card" style="border-color:rgba(0,240,255,.2);">
                    <div style="font-family:'Orbitron',sans-serif;font-size:.78rem;font-weight:700;color:#00f0ff;margin-bottom:8px;">
                        🚶 VULNERABLE ROAD USER (VRU) GUARDIAN
                    </div>
                    <div style="font-family:'JetBrains Mono',monospace;font-size:.72rem;line-height:1.9;">
                        Pedestrians: <strong style="color:#eab308;">{_vru['pedestrians_detected']} in crosswalk</strong><br>
                        Status: <strong style="color:#10b981;">{_vru['crosswalk_status']}</strong><br>
                        WALK Timer: <strong style="color:#a855f7;">{_vru['recommended_walk_seconds']}s (Ext: +{_vru['walk_extension_seconds']}s)</strong>
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )
        except Exception:
            st.warning("VRU safety module offline.")

    # ── ANPR + VIOLATIONS PREVIEW
    mini_separator()
    sec_div("🚘 ANPR REAL-TIME OCR · TRAFFIC VIOLATIONS PREVIEW")
    anpr_col, viol_col = st.columns(2)
    _scen_raw = data.get("scenario", "normal")
    token = st.session_state.get("jwt_token", "")
    headers = {"Authorization": f"Bearer {token}"}
    with anpr_col:
        try:
            _anpr = requests.get(
                f"{BACKEND}/api/v1/anpr/{_scen_raw}",
                params={
                    "latitude": st.session_state.get("latitude", 28.6315),
                    "longitude": st.session_state.get("longitude", 77.2167),
                    "location_name": st.session_state.get("location_name", "Delhi"),
                },
                headers=headers,
                timeout=10,
            ).json()
            _plates = _anpr.get("anpr_records", [])
            _cc = _anpr.get("summary", {}).get(
                "country_flag", st.session_state.get("country_flag", "🇮🇳")
            )
            if _plates:
                for _p in _plates[:5]:
                    st.markdown(
                        f'<div style="display:flex;justify-content:space-between;align-items:center;background:rgba(0,0,0,.2);border:1px solid rgba(255,255,255,.05);border-radius:6px;padding:6px 10px;margin-bottom:4px;">'
                        f'<span style="background:#fff;color:#000;font-family:\'JetBrains Mono\',monospace;font-weight:700;font-size:.78rem;padding:2px 6px;border-radius:3px;border:2px solid #000;">{_p.get("plate", "—")}</span>'
                        f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:.7rem;color:#00f0ff;">{_cc} {_p.get("vehicle_type", "Vehicle")}</span>'
                        f"</div>",
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No plates detected for this scenario.")
        except Exception:
            st.warning("ANPR offline — check backend.")
    with viol_col:
        try:
            _viols = requests.get(
                f"{BACKEND}/api/v1/violations/{_scen_raw}",
                params={
                    "latitude": st.session_state.get("latitude", 28.6315),
                    "longitude": st.session_state.get("longitude", 77.2167),
                    "location_name": st.session_state.get("location_name", "Delhi"),
                },
                headers=headers,
                timeout=10,
            ).json()
            _vlist = _viols.get("violations", [])
            if _vlist:
                for _v in _vlist[:5]:
                    _fine_disp = _v.get(
                        "fine_local",
                        f"{st.session_state.get('currency_symbol', '₹')}{_v.get('fine_amount', '—')}",
                    )
                    _flag_v = _v.get(
                        "country_flag", st.session_state.get("country_flag", "🇮🇳")
                    )
                    st.markdown(
                        f"<div style=\"font-family:'JetBrains Mono',monospace;font-size:.75rem;color:#f59e0b;margin-bottom:6px;\">"
                        f'⚠️ <strong>{_v.get("type", "—")}</strong> — {_v.get("vehicle_id", "Unknown")} | {_flag_v} {_fine_disp}'
                        f"</div>",
                        unsafe_allow_html=True,
                    )
            else:
                st.success("✅ No violations detected for this scenario.")
        except Exception:
            st.warning("Violations module offline — check backend.")

    # ── NEXTGEN COMMAND PROTOCOLS (v9.0.0) ──
    mini_separator()
    sec_div("🚀 NEXT-GEN COMMAND PROTOCOLS (v9.0.0) — V2I & UAV DISPATCH")
    st.markdown(
        """
    <div class="t-sub" style="margin-bottom:12px;">
        ADVANCED TACTICAL RESPONSE // RESTRICTED ACCESS
    </div>
    """,
        unsafe_allow_html=True,
    )

    cmd1, cmd2 = st.columns(2)
    with cmd1:
        st.markdown(
            '<div style="background:rgba(168,85,247,0.1); border:1px solid rgba(168,85,247,0.3); padding:16px; border-radius:8px; text-align:center;">',
            unsafe_allow_html=True,
        )
        if st.button(
            "🛸 DISPATCH UAV DRONE (MAVLINK)", use_container_width=True, type="primary"
        ):
            try:
                res = requests.post(
                    f"{BACKEND}/api/v1/nextgen/drone-dispatch",
                    json={
                        "incident_type": "HIGH_RISK_COLLISION",
                        "latitude": st.session_state.get("latitude", 28.63),
                        "longitude": st.session_state.get("longitude", 77.21),
                    },
                    headers=headers,
                    timeout=5,
                )
                if res.ok:
                    data = res.json()
                    st.success(
                        f"✅ UAV {data['uav_callsign']} DISPATCHED! ETA: {data['eta_seconds']}s"
                    )
                else:
                    st.error("Access Denied or Server Error.")
            except Exception:
                st.error("UAV Comm Link Offline.")
        st.markdown("</div>", unsafe_allow_html=True)

    with cmd2:
        st.markdown(
            '<div style="background:rgba(16,185,129,0.1); border:1px solid rgba(16,185,129,0.3); padding:16px; border-radius:8px; text-align:center;">',
            unsafe_allow_html=True,
        )
        if st.button(
            "🌊 ACTIVATE V2I GREEN WAVE", use_container_width=True, type="primary"
        ):
            try:
                res = requests.post(
                    f"{BACKEND}/api/v1/nextgen/v2i-preempt",
                    json={
                        "vehicle_id": "AMB-99-DEL",
                        "vehicle_type": "AMBULANCE",
                        "route_path": ["INT-1", "INT-2"],
                    },
                    headers=headers,
                    timeout=5,
                )
                if res.ok:
                    data = res.json()
                    st.success(
                        f"✅ GREEN WAVE ACTIVE. {data['cleared_intersections']} intersections cleared."
                    )
                else:
                    st.error("V2I Handshake Failed.")
            except Exception:
                st.error("V2I Grid Offline.")
        st.markdown("</div>", unsafe_allow_html=True)
