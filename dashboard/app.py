import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Aegis-MHR Control Panel", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] { background-color: #06090e !important; color: #d1d7de !important; }
    h1 { color: #00f0ff !important; font-family: 'Courier New', monospace; font-weight: 800; text-shadow: 0 0 10px rgba(0, 240, 255, 0.6); }
    h3, h5 { color: #ffb703 !important; font-family: 'Courier New', monospace; }
    .stButton>button { width: 100%; background: #111827 !important; border: 1px solid #00f0ff !important; color: #00f0ff !important; font-weight: bold !important; }
    .stButton>button:hover { background: #00f0ff !important; color: #06090e !important; box-shadow: 0 0 15px #00f0ff !important; }
    div[data-testid="stElementContainer"] div.stDataFrame { border: 1px solid #00f0ff; background-color: #0d1117; }
    div[data-testid="stMetricValue"] { font-family: monospace; font-size: 32px; color: #00f0ff !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ AEGIS-MHR // ENTERPRISE SECURITY CONSOLE")
st.caption("⚡ Live Production Multimodal Layer Engine • Distributed Thread Dispatch Grid")
st.markdown("---")

if "chat_history" not in st.session_state: st.session_state.chat_history = []

st.sidebar.markdown("<h2 style='color:#00f0ff; font-family:monospace;'>🕹️ ENGINE CONTROLS</h2>", unsafe_allow_html=True)
scenario = st.sidebar.selectbox("Select Target Stream Vector Profile:", ["Normal", "Accident", "Fire", "Tamper"])
model_tier = st.sidebar.selectbox("Active Inference Weights:", ["YOLOv8-Nano (Speed Edge Optimized)", "YOLOv8-XLarge (Precision High-Load)"])
vision_threshold = st.sidebar.slider("Dynamic Visual Cutoff Filter", 0.0, 1.0, 0.50)

st.sidebar.markdown("---")
deploy_btn = st.sidebar.button("ENGAGE LIVE DIAGNOSTIC STREAM", type="primary")

BACKEND_URL = "http://127.0.0.1:8000/api/v1/analyze"
HISTORY_URL = "http://127.0.0.1:8000/api/v1/history"
CHAT_URL = "http://127.0.0.1:8000/api/v1/chat"

if deploy_btn:
    try:
        res = requests.post(BACKEND_URL, json={"scenario": scenario.lower(), "vision_threshold": vision_threshold, "model_tier": model_tier})
        if res.status_code == 200: st.session_state.active_data = res.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Link Severed: Backend on port 8000 offline.")

if "active_data" in st.session_state:
    data = st.session_state.active_data
    alert_status = data["fusion_layer"]["alert_status"]
    dispatch_info = data["dispatch_network"]
    
    if "CRITICAL" in alert_status:
        st.markdown(f'<div style="background: linear-gradient(90deg, #7a0010 0%, #1a0004 100%); padding: 15px; border-left: 5px solid #ff003c; border-radius: 4px; margin-bottom: 20px;"><h4 style="margin:0; color:#ff3355; font-family:monospace;">🚨 INCIDENT DETECTED // {alert_status}</h4></div>', unsafe_allow_html=True)
    elif "TAMPER" in alert_status:
        st.markdown(f'<div style="background: linear-gradient(90deg, #d4a373 0%, #4a2c0f 100%); padding: 15px; border-left: 5px solid #ffb703; border-radius: 4px; margin-bottom: 20px;"><h4 style="margin:0; color:#ffb703; font-family:monospace;">⚠️ HARDWARE FAILURE ALERT // {alert_status}</h4></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="background: linear-gradient(90deg, #004b23 0%, #001508 100%); padding: 15px; border-left: 5px solid #38b000; border-radius: 4px; margin-bottom: 20px;"><h4 style="margin:0; color:#70e000; font-family:monospace;">✅ TELEMETRY MATRIX NOMINAL // PIPELINES SECURE</h4></div>', unsafe_allow_html=True)
        
    if dispatch_info["status"] != "STABLE":
        st.info(f"📡 Webhook Signal Dispatched: Real-world operational response teams notified via secure payload link!")

    m_col1, m_col2 = st.columns([1.8, 1.2])
    with m_col1:
        st.subheader("📊 Ingested Multi-Modal Stream Modules")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<p style='color:#ffb703; font-weight:bold;'>👁️ Vision Analytics Feeds</p>", unsafe_allow_html=True)
            df = pd.DataFrame(data["telemetry"]["visual_detections"])
            st.dataframe(df if not df.empty else pd.DataFrame(columns=["label", "confidence"]), use_container_width=True, hide_index=True)
        with c2:
            st.markdown("<p style='color:#ffb703; font-weight:bold;'>🔊 Acoustic Tracking Metrics</p>", unsafe_allow_html=True)
            aud = data["telemetry"]["acoustic_profile"]
            st.metric(label=f"Profile: {aud['type']}", value=f"{aud['db_level']} dB", delta=f"{aud['status']}")
            
        # --- FEATURE 2: HISTORICAL TIME-SERIES VISUALIZER ---
        st.markdown("<p style='color:#ffb703; font-weight:bold; margin-top:15px;'>📈 Enterprise Historical Threat Analytics Trend Ledger</p>", unsafe_allow_html=True)
        try:
            h_res = requests.get(HISTORY_URL).json()
            h_df = pd.DataFrame(h_res["history"])
            if not h_df.empty:
                fig = px.line(h_df, x="timestamp", y="risk_score", title="System Anomaly Threat Index Path", template="plotly_dark", markers=True)
                fig.update_layout(height=180, margin=dict(l=10, r=10, t=25, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                fig.update_traces(line_color="#00f0ff")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.caption("Awaiting initial telemetry logs to compile timeline graphic tracking arrays.")
        except Exception:
            st.caption("Unable to load transactional data streams.")
        
    with m_col2:
        st.subheader("🧠 Aegis Core Tactical Assistant Interface")
        chat_container = st.container(height=310)
        for msg in st.session_state.chat_history:
            with chat_container.chat_message(msg["role"]): st.markdown(msg["text"])
                
        user_input = st.chat_input("Query security parameters or prompt threat resolution steps...")
        if user_input:
            with chat_container.chat_message("user"): st.markdown(user_input)
            st.session_state.chat_history.append({"role": "user", "text": user_input})
            
            chat_res = requests.post(CHAT_URL, json={"user_message": user_input, "incident_context": data["fused_context"]}).json()
            ai_reply = chat_res["reply"]
            with chat_container.chat_message("assistant"): st.markdown(ai_reply)
            st.session_state.chat_history.append({"role": "assistant", "text": ai_reply})

    st.markdown("---")
    st.code(f"[{datetime.now().strftime('%H:%M:%S')}] Core Computing Core -> Latency: {data['latency_ms']} ms | Weight Profile: {model_tier}\n[{datetime.now().strftime('%H:%M:%S')}] Automated System Log -> {data['fusion_layer']['automated_incident_report']}", language="bash")