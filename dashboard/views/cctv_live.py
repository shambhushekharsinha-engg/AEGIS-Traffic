"""
AEGIS-Traffic Streamlit Dashboard — Real-Time CCTV Analytics Page
Enhanced v2: Multi-camera switcher, signal phase countdown, VRU guardian.
"""

import time

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

CAMERA_NODES = {
    "CAM-01 · Connaught Place (Primary)": {
        "id": "CAM-01",
        "location": "Connaught Place, New Delhi",
        "fps": 29.8,
        "latency_ms": 14.2,
        "tracks": 38,
        "phase": "North-South GREEN",
        "phase_remaining": 32,
        "phase_color": "#10b981",
        "pedestrians": 3,
        "counts": {
            "Cars": 22,
            "Trucks": 4,
            "Buses": 2,
            "Motorcycles": 8,
            "Pedestrians": 3,
        },
    },
    "CAM-02 · Rajpath Corridor": {
        "id": "CAM-02",
        "location": "Rajpath, New Delhi",
        "fps": 28.4,
        "latency_ms": 18.6,
        "tracks": 24,
        "phase": "East-West GREEN",
        "phase_remaining": 18,
        "phase_color": "#10b981",
        "pedestrians": 7,
        "counts": {
            "Cars": 14,
            "Trucks": 2,
            "Buses": 5,
            "Motorcycles": 12,
            "Pedestrians": 7,
        },
    },
    "CAM-03 · India Gate Junction": {
        "id": "CAM-03",
        "location": "India Gate, New Delhi",
        "fps": 30.0,
        "latency_ms": 11.9,
        "tracks": 51,
        "phase": "North-South RED",
        "phase_remaining": 45,
        "phase_color": "#ef4444",
        "pedestrians": 14,
        "counts": {
            "Cars": 31,
            "Trucks": 7,
            "Buses": 3,
            "Motorcycles": 19,
            "Pedestrians": 14,
        },
    },
    "CAM-04 · Lajpat Nagar Flyover": {
        "id": "CAM-04",
        "location": "Lajpat Nagar, New Delhi",
        "fps": 27.1,
        "latency_ms": 22.3,
        "tracks": 17,
        "phase": "Pedestrian Walk ACTIVE",
        "phase_remaining": 12,
        "phase_color": "#a855f7",
        "pedestrians": 22,
        "counts": {
            "Cars": 9,
            "Trucks": 1,
            "Buses": 1,
            "Motorcycles": 6,
            "Pedestrians": 22,
        },
    },
}


def render_cctv_live_page(client):
    st.markdown("### 📹 Real-Time CCTV & Object Tracking Analytics")
    st.caption(
        "Live frame analysis powered by OpenCV, YOLOv8 vehicle detection, and ByteTrack object tracking."
    )

    # ── MULTI-CAMERA SWITCHER ─────────────────────────────────────────────────
    st.markdown(
        """
    <div style="font-family:'Orbitron',sans-serif;color:#00f0ff;font-size:.85rem;
                letter-spacing:2px;margin-bottom:8px;">
        📡 CAMERA NODE SELECTOR
    </div>
    """,
        unsafe_allow_html=True,
    )

    cam_cols = st.columns(len(CAMERA_NODES))
    if "selected_camera" not in st.session_state:
        st.session_state.selected_camera = list(CAMERA_NODES.keys())[0]

    def set_camera(cam_name):
        st.session_state.selected_camera = cam_name

    for col, cam_name in zip(cam_cols, CAMERA_NODES.keys()):
        cam = CAMERA_NODES[cam_name]
        is_active = st.session_state.selected_camera == cam_name
        border = (
            "border:2px solid #00f0ff;" if is_active else "border:1px solid #1e293b;"
        )
        col.markdown(
            f"""
        <div style="background:#0f172a;{border}border-radius:10px;padding:10px;
                    text-align:center;cursor:pointer;margin-bottom:4px;">
            <div style="color:#00f0ff;font-family:'Orbitron',sans-serif;
                        font-size:.65rem;font-weight:700;">{cam['id']}</div>
            <div style="color:#64748b;font-size:.6rem;margin-top:2px;">{cam['location'][:20]}</div>
            <div style="margin-top:6px;">
                <span style="background:#10b981;border-radius:50%;
                             display:inline-block;width:8px;height:8px;"></span>
                <span style="color:#a7f3d0;font-size:.6rem;"> LIVE</span>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )
        col.button(
            f"Select",
            key=f"cam_btn_{cam['id']}",
            on_click=set_camera,
            args=(cam_name,),
            use_container_width=True,
        )

    st.markdown("---")

    # ── ACTIVE CAMERA DATA ────────────────────────────────────────────────────
    cam_data = CAMERA_NODES[st.session_state.selected_camera]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Active Camera", cam_data["id"], cam_data["location"][:20])
    col2.metric("YOLO FPS", f"{cam_data['fps']} FPS", "+1.2 FPS")
    col3.metric("Inference Latency", f"{cam_data['latency_ms']} ms", "-0.8 ms")
    col4.metric("Active Vehicle Tracks", f"{cam_data['tracks']} Tracks")

    st.markdown("---")

    col_chart, col_details = st.columns([1.5, 1])

    with col_chart:
        df_classes = pd.DataFrame(
            [{"Vehicle Class": k, "Count": v} for k, v in cam_data["counts"].items()]
        )
        fig = px.bar(
            df_classes,
            x="Vehicle Class",
            y="Count",
            color="Vehicle Class",
            title=f"Live Vehicle Class Distribution — {cam_data['id']}",
            color_discrete_sequence=[
                "#00f0ff",
                "#a855f7",
                "#10b981",
                "#eab308",
                "#f97316",
            ],
        )
        fig.update_layout(
            template="plotly_dark",
            height=320,
            showlegend=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_details:
        # ── SIGNAL PHASE COUNTDOWN ────────────────────────────────────────────
        st.markdown("#### 🚦 Signal Phase Countdown")
        remaining = cam_data["phase_remaining"]
        phase = cam_data["phase"]
        phase_color = cam_data["phase_color"]
        max_phase = 60

        # Progress bar representing time remaining
        progress_pct = remaining / max_phase
        bar_color = phase_color

        st.markdown(
            f"""
        <div style="background:#0f172a;border:1px solid {bar_color};border-radius:10px;
                    padding:16px;margin-bottom:12px;">
            <div style="font-family:'Orbitron',sans-serif;color:{bar_color};
                        font-size:.75rem;margin-bottom:8px;">{phase}</div>
            <div style="font-family:'JetBrains Mono',monospace;color:{bar_color};
                        font-size:2.2rem;font-weight:700;">{remaining}s</div>
            <div style="font-size:.65rem;color:#64748b;margin-top:2px;">REMAINING IN PHASE</div>
            <div style="background:#1e293b;border-radius:4px;height:6px;margin-top:10px;">
                <div style="background:{bar_color};width:{int(progress_pct*100)}%;
                            height:6px;border-radius:4px;
                            transition:width 1s;"></div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # ── VRU PEDESTRIAN GUARDIAN ───────────────────────────────────────────
        st.markdown("#### 🚶 VRU Pedestrian Guardian")
        ped_count = cam_data["pedestrians"]
        ped_risk = "HIGH" if ped_count > 10 else ("MEDIUM" if ped_count > 5 else "LOW")
        ped_color = (
            "#ef4444"
            if ped_risk == "HIGH"
            else ("#eab308" if ped_risk == "MEDIUM" else "#10b981")
        )
        walk_ext = max(0, (ped_count - 3) * 2)

        st.markdown(
            f"""
        <div style="background:#0f172a;border:1px solid {ped_color};border-radius:10px;padding:12px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                <span style="color:#e2e8f0;font-size:.75rem;">Pedestrians Detected</span>
                <span style="color:{ped_color};font-weight:700;">{ped_count}</span>
            </div>
            <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                <span style="color:#e2e8f0;font-size:.75rem;">Risk Level</span>
                <span style="color:{ped_color};font-weight:700;">{ped_risk}</span>
            </div>
            <div style="display:flex;justify-content:space-between;">
                <span style="color:#e2e8f0;font-size:.75rem;">Walk Extension</span>
                <span style="color:#a855f7;font-weight:700;">+{walk_ext}s</span>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ── MULTI-CAMERA GRID SUMMARY ─────────────────────────────────────────────
    st.markdown(
        "<div style=\"font-family:'Orbitron',sans-serif;color:#00f0ff;"
        'font-size:.85rem;letter-spacing:2px;margin-bottom:12px;">'
        "📊 ALL CAMERA NODES OVERVIEW</div>",
        unsafe_allow_html=True,
    )
    summary_rows = []
    for name, cam in CAMERA_NODES.items():
        total_vehicles = sum(v for k, v in cam["counts"].items() if k != "Pedestrians")
        summary_rows.append(
            {
                "Camera": cam["id"],
                "Location": cam["location"],
                "FPS": cam["fps"],
                "Latency (ms)": cam["latency_ms"],
                "Active Phase": cam["phase"],
                "Phase Remaining (s)": cam["phase_remaining"],
                "Vehicles": total_vehicles,
                "Pedestrians": cam["pedestrians"],
            }
        )
    st.dataframe(
        pd.DataFrame(summary_rows),
        use_container_width=True,
        hide_index=True,
    )
