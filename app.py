import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Aegis-MHR Tactical HUD", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #06090e !important;
        color: #d1d7de !important;
    }
    h1 { 
        color: #00f0ff !important; 
        font-family: 'Courier New', monospace; 
        font-weight: 800;
        text-shadow: 0 0 10px rgba(0, 240, 255, 0.6);
    }
    h3, h5 { color: #ffb703 !important; font-family: 'Courier New', monospace; }
    .stButton>button { 
        width: 100%; background: #111827 !important; border: 1px solid #00f0ff !important; color: #00f0ff !important; font-weight: bold !important;
    }
    .stButton>button:hover { background: #00f0ff !important; color: #06090e !important; box-shadow: 0 0 15px #00f0ff !important; }
    div[data-testid="stElementContainer"] div.stDataFrame { border: 1px solid #00f0ff; background-color: #0d1117; }
    div[data-testid="stMetricValue"] { font-family: monospace; font-size: 32px; color: #00f0ff !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ AEGIS-MHR // TACTICAL INTELLIGENCE HUD")
st.caption("⚡ Enterprise Threat Network Framework • Active Local Transformer Pipelines")
st.markdown("---")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "active_context" not in st.session_state:
    st.session_state.active_context = "Monitoring frameworks standing nominal."

# Sidebar Operations Deck
st.sidebar.markdown("<h2 style='color:#00f0ff; font-family:monospace;'>🕹️ HUD ENGINE CONTROLS</h2>", unsafe_allow_html=True)
scenario = st.sidebar.selectbox("Select Target Stream Vector Profile:", ["Normal", "Accident", "Fire", "Tamper"])

# Feature 2: UI Model Weight Switching Dropdown
model_tier = st.sidebar.selectbox("Active AI Inference Weights:", ["YOLOv8-Nano (Speed Edge Optimized)", "YOLOv8-XLarge (Precision High-Load)"])

# Feature 1: Dynamic Model Sensitivity Sliders
vision_threshold = st.sidebar.slider("YOLO Visual Core Threshold Cutoff", 0.0, 1.0, 0.50)

st.sidebar.markdown("---")
deploy_btn = st.sidebar.button("ENGAGE LIVE DIAGNOSTIC STREAM", type="primary")

if st.sidebar.button("RESET TACTICAL DATA LOGS"):
    st.session_state.chat_history = []
    st.session_state.pop("active_data", None)
    st.rerun()

BACKEND_URL = "http://127.0.0.1:8000/api/v1/analyze"
CHAT_URL = "http://127.0.0.1:8000/api/v1/chat"

if deploy_btn:
    with st.spinner("Synchronizing algorithmic pipelines..."):
        try:
            payload = {"scenario": scenario.lower(), "vision_threshold": vision_threshold, "model_tier": model_tier}
            res = requests.post(BACKEND_URL, json=payload)
            if res.status_code == 200:
                st.session_state.active_data = res.json()
                st.session_state.active_context = res.json()["fused_context"]
        except requests.exceptions.ConnectionError:
            st.error("❌ Transmission Severed: FastAPI backend engine on port 8000 is offline.")

if "active_data" in st.session_state:
    data = st.session_state.active_data
    alert_status = data["fusion_layer"]["alert_status"]
    dispatch_info = data["dispatch_network"]
    
    # Render Custom Dynamic UI Alert Banners
    if "CRITICAL" in alert_status:
        st.markdown(f'<div style="background: linear-gradient(90deg, #7a0010 0%, #1a0004 100%); padding: 15px; border-left: 5px solid #ff003c; border-radius: 4px; margin-bottom: 20px;"><h4 style="margin:0; color:#ff3355; font-family:monospace;">🚨 DETECTED HAZARD INCIDENT COMPROMISE // {alert_status}</h4></div>', unsafe_allow_html=True)
    elif "TAMPER" in alert_status:
        st.markdown(f'<div style="background: linear-gradient(90deg, #d4a373 0%, #4a2c0f 100%); padding: 15px; border-left: 5px solid #ffb703; border-radius: 4px; margin-bottom: 20px;"><h4 style="margin:0; color:#ffb703; font-family:monospace;">⚠️ HARDWARE FAILURE ALERT DETECTED // {alert_status}</h4></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="background: linear-gradient(90deg, #004b23 0%, #001508 100%); padding: 15px; border-left: 5px solid #38b000; border-radius: 4px; margin-bottom: 20px;"><h4 style="margin:0; color:#70e000; font-family:monospace;">✅ NETWORK MATRIX NOMINAL // PIPELINES SECURE</h4></div>', unsafe_allow_html=True)
        
    # Feature 4: Dynamic Threaded Alert Status Tracker Dashboard Component
    if dispatch_info["status"] != "STABLE":
        st.info(f"📡 Asynchronous Network Broadcast: {dispatch_info['last_broadcast'] if dispatch_info['status'] == 'SUCCESS' else 'Deploying remote encrypted crisis packets...'}")

    m_col1, m_col2 = st.columns([1.8, 1.2])
    
    with m_col1:
        st.subheader("📊 Ingested Multi-Modal Stream Modules")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<p style='color:#ffb703; font-weight:bold; margin-bottom:2px;'>👁️ Vision Processing Grid Feed</p>", unsafe_allow_html=True)
            df = pd.DataFrame(data["telemetry"]["visual_detections"])
            if df.empty:
                st.caption("⚠️ No objects matched active threshold limits.")
            else:
                st.dataframe(df, use_container_width=True, hide_index=True)
        with c2:
            st.markdown("<p style='color:#ffb703; font-weight:bold; margin-bottom:2px;'>🔊 Acoustic Signal Decibel Array</p>", unsafe_allow_html=True)
            aud = data["telemetry"]["acoustic_profile"]
            st.metric(label=f"Acoustic Variant: {aud['type']}", value=f"{aud['db_level']} dB", delta=f"Channel: {aud['status']}")
            
        st.markdown("<p style='color:#ffb703; font-weight:bold; margin-top:15px; margin-bottom:2px;'>📈 Computational Engine Metrics</p>", unsafe_allow_html=True)
        m_df = pd.DataFrame({
            "Core Pipeline Metric": ["Execution Latency (ms)", "Threat Index Score (%)"],
            "Telemetry Value": [data["latency_ms"], data["risk_score"]]
        })
        fig = px.bar(m_df, x="Core Pipeline Metric", y="Telemetry Value", color="Core Pipeline Metric", text_auto=True, template="plotly_dark", color_discrete_map={"Execution Latency (ms)": "#00f0ff", "Threat Index Score (%)": "#ff3355"})
        fig.update_layout(showlegend=False, height=210, margin=dict(l=20, r=20, t=15, b=15), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
        
    with m_col2:
        st.subheader("🧠 Aegis Tactical AI Assistant")
        chat_container = st.container(height=280)
        for msg in st.session_state.chat_history:
            with chat_container.chat_message(msg["role"]):
                st.markdown(msg["text"])
                
        user_input = st.chat_input("Query security parameters or tactical response guidance...")
        if user_input:
            with chat_container.chat_message("user"):
                st.markdown(user_input)
            st.session_state.chat_history.append({"role": "user", "text": user_input})
            
            chat_res = requests.post(CHAT_URL, json={"user_message": user_input, "incident_context": st.session_state.active_context}).json()
            ai_reply = chat_res["reply"]
            with chat_container.chat_message("assistant"):
                st.markdown(ai_reply)
            st.session_state.chat_history.append({"role": "assistant", "text": ai_reply})

    st.markdown("---")
    st.code(f"[{datetime.now().strftime('%H:%M:%S')}] Active Context Registry -> {st.session_state.active_context}\n[{datetime.now().strftime('%H:%M:%S')}] Computing Thread Performance Profile -> Latency: {data['latency_ms']} ms | Weight Profile: {model_tier}", language="bash")
else:
    st.info("💡 Sensor Array Online. Ingest a stream vector simulation module from the left HUD panel deck to initiate structural telemetry parsing.")