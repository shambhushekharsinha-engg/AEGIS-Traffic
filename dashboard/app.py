import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# Page configuration for a true widescreen operations dashboard
st.set_page_config(page_title="AEGIS-MHR // Operational Command Deck", page_icon="🛡️", layout="wide")

# Enhanced visual theme injection: Cyberpunk Dark Mode Matrix
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Share+Tech+Mono&display=swap');
    
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background: radial-gradient(circle at top right, #0a1128, #020617) !important;
        color: #e2e8f0 !important;
    }
    
    /* Neon HUD Title Styling */
    .hud-title {
        font-family: 'Orbitron', sans-serif;
        color: #00f0ff;
        font-weight: 700;
        text-shadow: 0 0 15px rgba(0, 240, 255, 0.5);
        letter-spacing: 2px;
        margin-bottom: 5px;
    }
    
    .hud-subtitle {
        font-family: 'Share Tech Mono', monospace;
        color: #64748b;
        letter-spacing: 1px;
    }
    
    /* Premium Grid Cards */
    .metric-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(0, 240, 255, 0.15);
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        margin-bottom: 15px;
    }
    
    .metric-label {
        font-family: 'Share Tech Mono', monospace;
        color: #94a3b8;
        font-size: 0.85rem;
        text-transform: uppercase;
    }
    
    .metric-value {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.8rem;
        color: #ffffff;
        margin-top: 5px;
    }
    
    /* Interactive Button glow effects */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #0f172a, #1e293b) !important;
        border: 1px solid #00f0ff !important;
        color: #00f0ff !important;
        font-family: 'Orbitron', sans-serif;
        font-weight: bold !important;
        letter-spacing: 1px;
        transition: all 0.3s ease;
        padding: 10px 0;
        border-radius: 6px;
    }
    .stButton>button:hover {
        background: #00f0ff !important;
        color: #020617 !important;
        box-shadow: 0 0 20px rgba(0, 240, 255, 0.6) !important;
        transform: translateY(-2px);
    }
    
    /* Custom Scannable Dataframes */
    div[data-testid="stElementContainer"] div.stDataFrame {
        border: 1px solid rgba(0, 240, 255, 0.2);
        background-color: #0b1329;
        border-radius: 6px;
    }
    </style>
    
    <script src="https://unpkg.com/lucide@latest"></script>
""", unsafe_allow_html=True)

# HUD Top Header Construction
st.markdown('<h1 class="hud-title">🛡️ AEGIS-MHR // NEXT-GEN HUD SECURITY OPERATOR</h1>', unsafe_allow_html=True)
st.markdown('<p class="hud-subtitle">🤖 Enterprise Threat Network Framework • Active Local Transformer Architecture</p>', unsafe_allow_html=True)
st.markdown("<hr style='border: 0.5px solid rgba(0, 240, 255, 0.15);'>", unsafe_allow_html=True)

if "chat_history" not in st.session_state: st.session_state.chat_history = []

# Sidebar Operations Deck Configuration
st.sidebar.markdown("<h2 style='color:#00f0ff; font-family:Orbitron; font-size:1.2rem; letter-spacing:1px;'>🕹️ HUD CONTROL PANELS</h2>", unsafe_allow_html=True)
scenario = st.sidebar.selectbox("🎯 Target Stream Profile Matrix:", ["Normal", "Accident", "Fire", "Tamper"])
model_tier = st.sidebar.selectbox("🧠 Engine Weights Matrix:", ["YOLOv8-Nano (Speed Edge Optimized)", "YOLOv8-XLarge (Precision High-Load)"])
vision_threshold = st.sidebar.slider("🎛️ Visual Core Sensor Cutoff Filter", 0.0, 1.0, 0.50)

st.sidebar.markdown("<br><hr style='border: 0.5px solid rgba(0, 240, 255, 0.15);'>", unsafe_allow_html=True)
deploy_btn = st.sidebar.button("⚡ ENGAGE PRODUCTION SIGNAL INGEST", type="primary")

BACKEND_URL = "http://127.0.0.1:8000/api/v1/analyze"
HISTORY_URL = "http://127.0.0.1:8000/api/v1/history"
CHAT_URL = "http://127.0.0.1:8000/api/v1/chat"

if deploy_btn:
    with st.spinner("Locking sensory pipelines..."):
        try:
            res = requests.post(BACKEND_URL, json={"scenario": scenario.lower(), "vision_threshold": vision_threshold, "model_tier": model_tier})
            if res.status_code == 200: st.session_state.active_data = res.json()
        except requests.exceptions.ConnectionError:
            st.error("❌ Transmission Failure: FastAPI network core offline.")

if "active_data" in st.session_state:
    data = st.session_state.active_data
    alert_status = data["fusion_layer"]["alert_status"]
    dispatch_info = data["dispatch_network"]
    
    # 🚨 Beautiful Corporate Layout Status Banners
    if "CRITICAL" in alert_status:
        st.markdown(f'<div style="background: linear-gradient(90deg, rgba(239, 68, 68, 0.25) 0%, rgba(127, 29, 29, 0.4) 100%); padding: 18px; border: 1px solid #ef4444; border-left: 6px solid #ef4444; border-radius: 6px; margin-bottom: 25px;"><h4 style="margin:0; color:#fca5a5; font-family:\'Orbitron\', sans-serif; font-size:1.1rem; letter-spacing:1px;">⚠️ DANGER: HIGH LEVEL INCIDENT COMPROMISE ACTIVE // {alert_status}</h4></div>', unsafe_allow_html=True)
    elif "TAMPER" in alert_status:
        st.markdown(f'<div style="background: linear-gradient(90deg, rgba(245, 158, 11, 0.25) 0%, rgba(146, 64, 14, 0.4) 100%); padding: 18px; border: 1px solid #f59e0b; border-left: 6px solid #f59e0b; border-radius: 6px; margin-bottom: 25px;"><h4 style="margin:0; color:#fde68a; font-family:\'Orbitron\', sans-serif; font-size:1.1rem; letter-spacing:1px;">🛡️ SYSTEM ALERT: CAMERA BLINDNESS OR HARDWARE DISCONNECTION // {alert_status}</h4></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="background: linear-gradient(90deg, rgba(16, 185, 129, 0.25) 0%, rgba(6, 78, 59, 0.4) 100%); padding: 18px; border: 1px solid #10b981; border-left: 6px solid #10b981; border-radius: 6px; margin-bottom: 25px;"><h4 style="margin:0; color:#a7f3d0; font-family:\'Orbitron\', sans-serif; font-size:1.1rem; letter-spacing:1px;">✅ MONITORING SYSTEM ONLINE: RUNNING baseline SCANS</h4></div>', unsafe_allow_html=True)
        
    if dispatch_info["status"] != "STABLE":
        st.markdown(f'<div style="background: rgba(30, 41, 59, 0.8); border: 1px dashed #00f0ff; padding: 12px; border-radius: 6px; margin-bottom: 20px; font-family:\'Share Tech Mono\', monospace; color: #00f0ff;">📡 [COMMUNICATION ARRAY]: {dispatch_info["last_broadcast"] if dispatch_info["status"] == "SUCCESS" else "Deploying emergency network packets across communication links..."}</div>', unsafe_allow_html=True)

    # 📈 Custom Professional Core KPI Row
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">⏱️ Core Engine Latency</div><div class="metric-value" style="color:#00f0ff;">{data["latency_ms"]}<span style="font-size:1rem; color:#64748b;"> ms</span></div></div>', unsafe_allow_html=True)
    with kpi2:
        color_map = "#ef4444" if data["risk_score"] > 70 else ("#f59e0b" if data["risk_score"] > 30 else "#10b981")
        st.markdown(f'<div class="metric-card"><div class="metric-label">⚡ Threat Risk Rating</div><div class="metric-value" style="color:{color_map};">{data["risk_score"]}<span style="font-size:1rem; color:#64748b;"> %</span></div></div>', unsafe_allow_html=True)
    with kpi3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">🔊 Acoustic Pressure</div><div class="metric-value" style="color:#ffb703;">{data["telemetry"]["acoustic_profile"]["db_level"]}<span style="font-size:1rem; color:#64748b;"> dB</span></div></div>', unsafe_allow_html=True)
    with kpi4:
        st.markdown(f'<div class="metric-card"><div class="metric-label">🧠 Decision Engine</div><div class="metric-value" style="color:#a855f7; font-size:1.1rem; padding-top:12px; font-family:\'Share Tech Mono\';">DistilBERT Fused Core</div></div>', unsafe_allow_html=True)

    # Split Main Operations HUD View Layout Grid
    m_col1, m_col2 = st.columns([1.7, 1.3])
    
    with m_col1:
        st.markdown("<h3 style='font-size:1.2rem; margin-bottom:10px;'>📊 Multi-Sensory Pipeline Feeds</h3>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<p style='color:#00f0ff; font-family:\"Share Tech Mono\"; font-weight:bold; margin-bottom:5px;'>👁️ Object Recognition Matrix</p>", unsafe_allow_html=True)
            df = pd.DataFrame(data["telemetry"]["visual_detections"])
            st.dataframe(df if not df.empty else pd.DataFrame(columns=["label", "confidence"]), use_container_width=True, hide_index=True)
        with c2:
            st.markdown("<p style='color:#00f0ff; font-family:\"Share Tech Mono\"; font-weight:bold; margin-bottom:5px;'>🔊 Acoustic Diagnostics Status</p>", unsafe_allow_html=True)
            aud = data["telemetry"]["acoustic_profile"]
            st.markdown(f"""
                <div style="background:rgba(15,23,42,0.6); border:1px solid rgba(0,240,255,0.1); padding:15px; border-radius:6px; font-family:'Share Tech Mono', monospace;">
                    <p style="margin:0 0 8px 0;">Signal Profile: <span style="color:#ffb703;">{aud['type']}</span></p>
                    <p style="margin:0;">Sensory Status: <span style="color:#10b981;">{aud['status']}</span></p>
                </div>
            """, unsafe_allow_html=True)
            
        # Time-Series Analytics Ledger Charts component
        st.markdown("<p style='color:#00f0ff; font-family:\"Share Tech Mono\"; font-weight:bold; margin-top:20px;'>📈 Long-Term Time-Series Incident Matrix Trend Logs</p>", unsafe_allow_html=True)
        try:
            h_res = requests.get(HISTORY_URL).json()
            h_df = pd.DataFrame(h_res["history"])
            if not h_df.empty:
                fig = px.line(h_df, x="timestamp", y="risk_score", template="plotly_dark", markers=True)
                fig.update_layout(height=180, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                fig.update_traces(line_color="#00f0ff", marker=dict(color="#a855f7", size=6))
                st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.caption("Awaiting initial telemetry logs pipeline connection traces.")
        
    with m_col2:
        st.markdown("<h3 style='font-size:1.2rem; margin-bottom:10px;'>🧠 Tactical Crisis Response AI Assistant</h3>", unsafe_allow_html=True)
        chat_container = st.container(height=325)
        for msg in st.session_state.chat_history:
            with chat_container.chat_message(msg["role"]): st.markdown(msg["text"])
                
        user_input = st.chat_input("Query threat tracking signatures or prompt containment protocols...")
        if user_input:
            with chat_container.chat_message("user"): st.markdown(user_input)
            st.session_state.chat_history.append({"role": "user", "text": user_input})
            
            chat_res = requests.post(CHAT_URL, json={"user_message": user_input, "incident_context": data["fused_context"]}).json()
            ai_reply = chat_res["reply"]
            with chat_container.chat_message("assistant"): st.markdown(ai_reply)
            st.session_state.chat_history.append({"role": "assistant", "text": ai_reply})

    st.markdown("<hr style='border: 0.5px solid rgba(0, 240, 255, 0.15);'>", unsafe_allow_html=True)
    st.code(f"// Active Telemetry Registry Log Matrix Buffer\n[{datetime.now().strftime('%H:%M:%S')}] Core Processing Node -> Weights: {model_tier}\n[{datetime.now().strftime('%H:%M:%S')}] Neural Synthesis Report -> {data['fusion_layer']['automated_incident_report']}", language="javascript")
else:
    st.info("💡 Sensor Ingestion Offline. Select a streaming data profile vector from the left operations dashboard panel and engage parameters to populate active telemetry pipelines.")