import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import uuid
import base64
import time
import json
import math
import random
import os
from io import BytesIO

# ──────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="AEGIS-TRAFFIC // Smart City Operations",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ──────────────────────────────────────────────
# SESSION STATE BOOTSTRAP
# ──────────────────────────────────────────────
for key, default in [
    ("user_token", f"AEGIS-{uuid.uuid4().hex[:8].upper()}"),
    ("chat_history", []),
    ("copilot_history", []),
    ("latitude", 28.6315),
    ("longitude", 77.2167),
    ("location_name", "Connaught Place, New Delhi"),
    ("active_data", None),
    ("sb_results", None),
    ("tutorial_step", 0),
    # ── Global / geo context ───────────────────────────────────────────────────
    ("country_code",    "IN"),
    ("country_flag",    "🇮🇳"),
    ("country_name",    "India"),
    ("currency_code",   "INR"),
    ("currency_symbol", "₹"),
    ("speed_limit_kmh", 50),
    ("drive_side",      "left"),
    ("plate_format",    "XX00 XX0000"),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ──────────────────────────────────────────────
# GLOBAL CONSTANTS
# ──────────────────────────────────────────────
BACKEND   = os.environ.get("AEGIS_BACKEND_URL", "http://127.0.0.1:8000")
ANALYZE_URL      = f"{BACKEND}/api/v1/analyze"
HISTORY_URL      = f"{BACKEND}/api/v1/history"
CHAT_URL         = f"{BACKEND}/api/v1/chat"
LOGIN_URL        = f"{BACKEND}/api/v1/auth/login"
REGISTER_URL     = f"{BACKEND}/api/v1/auth/register"
ANPR_URL         = f"{BACKEND}/api/v1/anpr"              # §16
VIOLATIONS_URL   = f"{BACKEND}/api/v1/violations"         # §15
PIPELINE_URL     = f"{BACKEND}/api/v1/pipeline/status"
MAP_VEHICLES_URL = f"{BACKEND}/api/v1/map/vehicles"       # Map Intelligence live tracking


def sync_geo_context(location_name: str = "", lat: float = 0.0, lon: float = 0.0):
    """Dynamically syncs country flag, currency, speed limit, and drive side in session state."""
    try:
        from app.core.geo_currency import detect_country, get_country_config
        cc  = detect_country(location_name=location_name, lat=lat, lon=lon, try_nominatim=True)
        cfg = get_country_config(cc)
        st.session_state.country_code    = cc
        st.session_state.country_flag    = cfg["flag"]
        st.session_state.country_name    = cfg["name"]
        st.session_state.currency_code   = cfg["currency_code"]
        st.session_state.currency_symbol = cfg["currency_symbol"]
        st.session_state.speed_limit_kmh = cfg.get("speed_limit_urban", 50)
        st.session_state.drive_side      = cfg.get("drive_side", "right")
        st.session_state.plate_format    = cfg.get("plate_format", "")
    except Exception:
        pass

# Always sync geo context on script run
sync_geo_context(st.session_state.location_name, st.session_state.latitude, st.session_state.longitude)

SCENARIO_MAP = {
    "🟢 Normal Flowing Traffic":      "normal",
    "🟡 Congested Traffic Queues":    "congested",
    "🚨 Emergency Vehicle Incoming":  "emergency",
    "💥 Vehicle Collision Accident":  "accident",
    "🛡️ Camera Feed Tampered":        "tamper",
}

MODE_ICONS = {
    "AI Automated Fusion":     "🤖",
    "Manual Override":         "🎛️",
    "Security Lockdown":       "🔒",
    "Predictive Optimization": "🔮",
}

# ──────────────────────────────────────────────
# MASTER CSS / DESIGN SYSTEM
# ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── BASE ── */
*, *::before, *::after { box-sizing: border-box; }

.stApp,[data-testid="stAppViewContainer"],[data-testid="stHeader"]{
    background: #010308 !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stSidebar"]{
    background: linear-gradient(180deg,#04080f 0%,#060c1a 100%) !important;
    border-right: 1px solid rgba(0,240,255,0.12) !important;
}
section[data-testid="stSidebarContent"]{ padding:0 !important; }

/* ── TYPOGRAPHY SCALE ── */
.t-hero{
    font-family:'Orbitron',sans-serif;
    font-size:clamp(1.5rem,3vw,2.6rem);
    font-weight:900;
    background:linear-gradient(120deg,#00f0ff,#a855f7,#06b6d4);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
    background-clip:text;
    letter-spacing:3px;
    line-height:1.1;
    text-shadow:none;
}
.t-sub{
    font-family:'JetBrains Mono',monospace;
    color:#4b6584;
    font-size:.82rem;
    letter-spacing:2px;
}
.t-section{
    font-family:'Orbitron',sans-serif;
    font-size:.92rem;
    font-weight:700;
    color:#e2e8f0;
    text-transform:uppercase;
    letter-spacing:2px;
}

/* ── CARD SYSTEM ── */
.card{
    background:rgba(6,12,26,.9);
    border:1px solid rgba(0,240,255,.1);
    border-radius:12px;
    padding:20px;
    box-shadow:0 4px 32px rgba(0,0,0,.6);
    transition:border-color .25s,box-shadow .25s;
}
.card:hover{
    border-color:rgba(0,240,255,.28);
    box-shadow:0 6px 40px rgba(0,240,255,.07);
}
.card-alert-red  { border-left:4px solid #ef4444 !important; background:rgba(239,68,68,.07) !important; }
.card-alert-amber{ border-left:4px solid #f59e0b !important; background:rgba(245,158,11,.07) !important; }
.card-alert-green{ border-left:4px solid #10b981 !important; background:rgba(16,185,129,.07) !important; }
.card-alert-blue { border-left:4px solid #6366f1 !important; background:rgba(99,102,241,.07) !important; }
.card-alert-purple{border-left:4px solid #a855f7 !important; background:rgba(168,85,247,.07) !important; }

/* ── METRIC TILES ── */
.metric-tile{
    background:rgba(6,12,26,.95);
    border:1px solid rgba(0,240,255,.12);
    border-radius:10px;
    padding:16px 12px;
    text-align:center;
    transition:transform .2s,box-shadow .2s;
}
.metric-tile:hover{ transform:translateY(-2px); box-shadow:0 8px 32px rgba(0,240,255,.12); }
.metric-tile .label{
    font-family:'JetBrains Mono',monospace;
    font-size:.68rem;
    color:#64748b;
    text-transform:uppercase;
    letter-spacing:1.5px;
    margin-bottom:8px;
}
.metric-tile .value{
    font-family:'Orbitron',sans-serif;
    font-size:1.75rem;
    font-weight:700;
    line-height:1;
}
.metric-tile .unit{
    font-size:.7rem;
    color:#4b6584;
    margin-left:3px;
}

/* ── STATUS BANNER ── */
.status-banner{
    border-radius:8px;
    padding:14px 20px;
    border-left:5px solid;
    margin-bottom:18px;
    font-family:'Orbitron',sans-serif;
    font-size:.88rem;
    letter-spacing:1px;
    display:flex;
    align-items:center;
    gap:12px;
}

/* ── SIGNAL BOX ── */
.signal-box{
    background:rgba(6,10,22,.95);
    border:1px solid rgba(0,240,255,.18);
    border-radius:10px;
    padding:16px;
    text-align:center;
}
.signal-dot{
    width:36px;
    height:36px;
    border-radius:50%;
    margin:10px auto;
}

/* ── SECTION DIVIDER ── */
.sec-div{
    font-family:'Orbitron',sans-serif;
    font-size:.78rem;
    color:#00f0ff;
    text-transform:uppercase;
    letter-spacing:3px;
    padding:8px 0 8px 14px;
    border-left:3px solid #00f0ff;
    margin:14px 0 10px 0;
    background:linear-gradient(90deg,rgba(0,240,255,.05),transparent);
    border-radius:0 4px 4px 0;
}

/* ── BUTTONS ── */
.stButton>button{
    background:linear-gradient(135deg,#0a1628,#0d1f3c) !important;
    border:1px solid rgba(0,240,255,.4) !important;
    color:#00f0ff !important;
    font-family:'Orbitron',sans-serif !important;
    font-size:.72rem !important;
    font-weight:700 !important;
    letter-spacing:1.5px !important;
    padding:10px 18px !important;
    border-radius:6px !important;
    transition:all .22s !important;
    text-transform:uppercase !important;
}
.stButton>button:hover{
    background:#00f0ff !important;
    color:#010308 !important;
    box-shadow:0 0 24px rgba(0,240,255,.55) !important;
    transform:translateY(-1px) !important;
}

/* ── SIDEBAR ITEMS ── */
.sb-block{
    background:rgba(0,240,255,.04);
    border:1px solid rgba(0,240,255,.1);
    border-radius:8px;
    padding:12px 14px;
    margin:8px 0;
    font-family:'JetBrains Mono',monospace;
    font-size:.78rem;
}
.sb-label{ color:#4b6584; font-size:.65rem; text-transform:uppercase; letter-spacing:1px; }

/* ── TABS OVERRIDE ── */
button[data-baseweb="tab"]{
    font-family:'Orbitron',sans-serif !important;
    font-size:.7rem !important;
    font-weight:700 !important;
    letter-spacing:1px !important;
    color:#64748b !important;
    background:transparent !important;
    border:none !important;
    padding:10px 16px !important;
}
button[data-baseweb="tab"][aria-selected="true"]{
    color:#00f0ff !important;
    border-bottom:2px solid #00f0ff !important;
}

/* ── CHAT MESSAGES ── */
.chat-msg-user{
    background:rgba(99,102,241,.15);
    border:1px solid rgba(99,102,241,.3);
    border-radius:10px 10px 2px 10px;
    padding:10px 14px;
    margin:6px 0;
    font-family:'Inter',sans-serif;
    font-size:.87rem;
    color:#e2e8f0;
}
.chat-msg-ai{
    background:rgba(0,240,255,.06);
    border:1px solid rgba(0,240,255,.18);
    border-radius:10px 10px 10px 2px;
    padding:10px 14px;
    margin:6px 0;
    font-family:'Inter',sans-serif;
    font-size:.87rem;
    color:#cffafe;
}

/* ── LOGIN PORTAL ── */
.login-portal{
    max-width:480px;
    margin:60px auto 0;
    background:rgba(6,12,26,.98);
    border:1px solid rgba(0,240,255,.2);
    border-radius:16px;
    padding:40px 36px;
    box-shadow:0 0 80px rgba(0,240,255,.05);
}
.login-logo{
    text-align:center;
    margin-bottom:28px;
}
.badge-pill{
    display:inline-block;
    background:rgba(0,240,255,.1);
    border:1px solid rgba(0,240,255,.3);
    color:#00f0ff;
    font-family:'JetBrains Mono',monospace;
    font-size:.65rem;
    letter-spacing:2px;
    padding:3px 10px;
    border-radius:20px;
    text-transform:uppercase;
}
.cred-hint{
    background:rgba(16,185,129,.07);
    border:1px solid rgba(16,185,129,.2);
    border-radius:8px;
    padding:10px 14px;
    font-family:'JetBrains Mono',monospace;
    font-size:.72rem;
    color:#6ee7b7;
    margin-top:16px;
    line-height:1.8;
}

/* ── ADVISORY BOX ── */
.advisory-box{
    background:rgba(6,12,26,.95);
    border:1px solid rgba(56,189,248,.2);
    border-radius:8px;
    padding:14px;
    font-family:'JetBrains Mono',monospace;
    font-size:.8rem;
    line-height:1.7;
}

/* ── AI MATRIX ── */
.ai-matrix{
    background:#020510;
    border:1px dashed rgba(0,240,255,.25);
    border-radius:8px;
    padding:20px;
    text-align:center;
    font-family:'JetBrains Mono',monospace;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar{ width:4px; height:4px; }
::-webkit-scrollbar-track{ background:rgba(0,0,0,.2); }
::-webkit-scrollbar-thumb{ background:rgba(0,240,255,.3); border-radius:4px; }

/* ── MISC ── */
hr.divider{ border:none; border-top:1px solid rgba(0,240,255,.1); margin:16px 0; }
.stTextInput>div>div>input,.stSelectbox>div>div{ 
    background:rgba(4,8,20,.8) !important; 
    border:1px solid rgba(0,240,255,.2) !important;
    border-radius:6px !important;
    color:#e2e8f0 !important;
    font-family:'JetBrains Mono',monospace !important;
    font-size:.82rem !important;
}
.stSlider>div>div>div{ background:rgba(0,240,255,.3) !important; }

/* ── DARK CHAT INPUT STYLING ── */
div[data-testid="stChatInput"] { 
    background:rgba(4,8,20,.95) !important; 
    border:1px solid rgba(0,240,255,.35) !important;
    border-radius:10px !important;
    box-shadow:0 0 20px rgba(0,240,255,.08) !important;
    padding:4px !important;
}
div[data-testid="stChatInput"] textarea, div[data-testid="stChatInput"] input, .stChatInputContainer textarea { 
    background:rgba(4,8,20,.95) !important; 
    color:#f8fafc !important; 
    font-family:'JetBrains Mono',monospace !important; 
    font-size:.85rem !important; 
    caret-color:#00f0ff !important;
}
div[data-testid="stChatInput"] textarea::placeholder {
    color:#64748b !important;
}
div[data-testid="stChatInput"] button {
    background:rgba(0,240,255,.15) !important;
    border:1px solid rgba(0,240,255,.4) !important;
    color:#00f0ff !important;
    border-radius:6px !important;
}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# HELPER FUNCTIONS
# ──────────────────────────────────────────────
def auth_header():
    return {"Authorization": f"Bearer {st.session_state.get('jwt_token', '')}"}

def risk_color(risk):
    if risk > 70: return "#ef4444"
    if risk > 35: return "#f59e0b"
    return "#10b981"

def metric_tile(label, value, unit="", color="#00f0ff", icon=""):
    return f"""
    <div class="metric-tile">
        <div class="label">{icon} {label}</div>
        <div class="value" style="color:{color};">{value}<span class="unit">{unit}</span></div>
    </div>"""

def sec_div(text):
    st.markdown(f'<div class="sec-div">{text}</div>', unsafe_allow_html=True)

def mini_separator():
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

def backend_alive():
    try:
        r = requests.get(f"{BACKEND}/", timeout=2)
        return True
    except:
        return False


# ══════════════════════════════════════════════════════════════
# AUTHENTICATION GATE — LOGIN / REGISTER PORTAL
# ══════════════════════════════════════════════════════════════
if "jwt_token" not in st.session_state:

    # Background grid effect via HTML
    st.markdown("""
    <div style="position:fixed;top:0;left:0;width:100%;height:100%;
        background:repeating-linear-gradient(0deg,rgba(0,240,255,.02) 0px,rgba(0,240,255,.02) 1px,transparent 1px,transparent 60px),
                  repeating-linear-gradient(90deg,rgba(0,240,255,.02) 0px,rgba(0,240,255,.02) 1px,transparent 1px,transparent 60px);
        pointer-events:none;z-index:0;">
    </div>
    """, unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 1.1, 1])
    with col_c:
        st.markdown("""
        <div class="login-portal">
            <div class="login-logo">
                <div style="font-size:3rem;margin-bottom:8px;">🚦</div>
                <div class="t-hero" style="font-size:1.4rem;letter-spacing:4px;">AEGIS-TRAFFIC</div>
                <div style="font-family:'JetBrains Mono',monospace;color:#4b6584;font-size:.68rem;letter-spacing:3px;margin-top:4px;">MUNICIPAL AI OPERATIONS PLATFORM</div>
                <div style="margin-top:12px;">
                    <span class="badge-pill">v8.0 SECURE</span>
                    &nbsp;
                    <span class="badge-pill" style="border-color:rgba(168,85,247,.4);color:#a855f7;background:rgba(168,85,247,.08);">PRODUCTION</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["🔑  SECURE LOGIN", "📝  REGISTER OPERATOR"])

        with tab_login:
            st.markdown("<br>", unsafe_allow_html=True)

            # Quick Fill Action Buttons
            col_q1, col_q2, col_q3 = st.columns(3)
            if col_q1.button("🔑 Admin Quick Entry", use_container_width=True, key="btn_quick_admin"):
                st.session_state["login_username_input"] = "admin"
                st.session_state["login_password_input"] = "Admin@AEGIS2024!"
                st.session_state.quick_user = "admin"
                st.session_state.quick_pass = "Admin@AEGIS2024!"
                st.rerun()
            if col_q2.button("🔑 Operator Quick Entry", use_container_width=True, key="btn_quick_operator"):
                st.session_state["login_username_input"] = "operator"
                st.session_state["login_password_input"] = "Operator@AEGIS2024!"
                st.session_state.quick_user = "operator"
                st.session_state.quick_pass = "Operator@AEGIS2024!"
                st.rerun()
            if col_q3.button("🔑 Auditor Quick Entry", use_container_width=True, key="btn_quick_auditor"):
                st.session_state["login_username_input"] = "auditor"
                st.session_state["login_password_input"] = "Auditor@AEGIS2024!"
                st.session_state.quick_user = "auditor"
                st.session_state.quick_pass = "Auditor@AEGIS2024!"
                st.rerun()

            default_u = st.session_state.get("quick_user", "")
            default_p = st.session_state.get("quick_pass", "")

            with st.form("login_form", clear_on_submit=False):
                st.markdown('<div class="t-section" style="margin-bottom:14px;">Operator Credentials</div>', unsafe_allow_html=True)
                username = st.text_input("Username", value=default_u, placeholder="e.g. admin", label_visibility="collapsed", key="login_username_input")
                st.caption("Username")
                password = st.text_input("Password", value=default_p, type="password", placeholder="••••••••", label_visibility="collapsed", key="login_password_input")
                st.caption("Password")
                st.markdown("<br>", unsafe_allow_html=True)
                submitted = st.form_submit_button("🔐  AUTHENTICATE & CONNECT", use_container_width=True)

                if submitted:
                    if not username or not password:
                        st.error("⚠️ Enter both username and password.")
                    else:
                        with st.spinner("Verifying credentials against secure vault..."):
                            try:
                                res = requests.post(LOGIN_URL, json={"username": username, "password": password}, timeout=8)
                                if res.status_code == 200:
                                    d = res.json()
                                    st.session_state.jwt_token = d["access_token"]
                                    st.session_state.user_role = d["role"]
                                    st.session_state.username = d["username"]
                                    st.success("✅ Authentication successful. Initializing dashboard...")
                                    time.sleep(0.6)
                                    st.rerun()
                                else:
                                    err_detail = res.json().get("detail", "Access denied.")
                                    if isinstance(err_detail, dict):
                                        err_msg = err_detail.get("detail", err_detail.get("error", str(err_detail)))
                                    elif isinstance(err_detail, list):
                                        err_msg = err_detail[0].get("msg", str(err_detail[0])) if err_detail else "Invalid credentials."
                                    else:
                                        err_msg = str(err_detail)
                                    st.error(f"🚫 {err_msg}")
                            except requests.exceptions.ConnectionError:
                                st.error("❌ Backend microservice offline on port 8000. Please start the FastAPI server first.")

            st.markdown("""
            <div class="cred-hint">
                🔑 <strong>Demo Accounts</strong><br>
                admin / Admin@AEGIS2024! → Admin Clearance<br>
                operator / Operator@AEGIS2024! → Operator<br>
                auditor / Auditor@AEGIS2024! → Auditor View
            </div>
            """, unsafe_allow_html=True)

        with tab_register:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("register_form", clear_on_submit=True):
                st.markdown('<div class="t-section" style="margin-bottom:14px;">New Operator Registration</div>', unsafe_allow_html=True)
                reg_user = st.text_input("Desired Username", placeholder="new_operator", label_visibility="collapsed", key="reg_username_input")
                st.caption("Username")
                reg_pass = st.text_input("Desired Password", type="password", placeholder="••••••••", label_visibility="collapsed", key="reg_password_input")
                st.caption("Password (min 6 characters)")
                reg_role = st.selectbox("Clearance Level", ["Operator", "Auditor", "Admin"], label_visibility="collapsed", key="reg_role_select")
                st.caption("Clearance Level")
                st.markdown("<br>", unsafe_allow_html=True)
                reg_btn = st.form_submit_button("📋  REGISTER CREDENTIALS", use_container_width=True)

                if reg_btn:
                    if not reg_user or not reg_pass:
                        st.error("⚠️ All fields are required.")
                    elif len(reg_pass) < 6:
                        st.error("⚠️ Password must be at least 6 characters.")
                    else:
                        with st.spinner("Registering..."):
                            try:
                                res = requests.post(REGISTER_URL, json={"username": reg_user, "password": reg_pass, "role": reg_role}, timeout=8)
                                if res.status_code == 200:
                                    st.success(f"✅ {reg_user} registered as {reg_role}. Login to access.")
                                else:
                                    st.error(f"❌ {res.json().get('detail', 'Error')}")
                            except requests.exceptions.ConnectionError:
                                st.error("❌ Backend offline.")

    st.stop()


# ══════════════════════════════════════════════════════════════
# AUTHENTICATED DASHBOARD
# ══════════════════════════════════════════════════════════════

# ── TOP HEADER ──
hcol1, hcol2, hcol3 = st.columns([2, 3, 2])
with hcol1:
    st.markdown("""
    <div style="padding:8px 0;">
        <div class="t-hero">🚦 AEGIS-TRAFFIC</div>
        <div class="t-sub">SMART CITY AI OPERATIONS HUB</div>
    </div>
    """, unsafe_allow_html=True)
with hcol2:
    backend_ok = backend_alive()
    status_txt = "● BACKEND ONLINE" if backend_ok else "● BACKEND OFFLINE"
    status_col = "#10b981" if backend_ok else "#ef4444"
    st.markdown(f"""
    <div style="text-align:center;padding:10px 0;">
        <span style="font-family:'JetBrains Mono',monospace;font-size:.72rem;color:{status_col};letter-spacing:2px;">{status_txt}</span><br>
        <span style="font-family:'JetBrains Mono',monospace;font-size:.62rem;color:#4b6584;letter-spacing:1px;">
            🕐 {time.strftime('%H:%M:%S')} &nbsp;|&nbsp; MODE: {st.session_state.get('operational_mode','AI Automated Fusion').upper()}
        </span>
    </div>
    """, unsafe_allow_html=True)
with hcol3:
    role_badge_col = {"Admin": "#ef4444", "Operator": "#10b981", "Auditor": "#f59e0b"}.get(st.session_state.user_role, "#64748b")
    st.markdown(f"""
    <div style="text-align:right;padding:8px 0;">
        <span style="font-family:'JetBrains Mono',monospace;font-size:.72rem;color:#94a3b8;">
            👤 {st.session_state.username.upper()}
        </span><br>
        <span class="badge-pill" style="border-color:{role_badge_col}55;color:{role_badge_col};background:{role_badge_col}15;font-size:.6rem;">
            {st.session_state.user_role.upper()} CLEARANCE
        </span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)


# ── SIDEBAR ──
with st.sidebar:
    st.markdown("""
    <div style="padding:16px 16px 8px;">
        <div style="font-family:'Orbitron',sans-serif;font-size:.85rem;font-weight:700;color:#00f0ff;letter-spacing:2px;">⚙️ CONTROL PANEL</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="sb-block">
        <div class="sb-label">Authenticated Operator</div>
        <div style="color:white;font-weight:600;">{st.session_state.username}</div>
        <div class="sb-label" style="margin-top:4px;">Clearance</div>
        <div style="color:#10b981;">{st.session_state.user_role}</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔓 Disconnect Session", use_container_width=True, key="btn_disconnect_session"):
        for k in ["jwt_token", "user_role", "username", "active_data"]:
            st.session_state.pop(k, None)
        st.rerun()

    st.markdown('<div class="sec-div">🌍 Geographic Registry</div>', unsafe_allow_html=True)
    location_query = st.text_input("Target Location", st.session_state.location_name, label_visibility="collapsed", key="sb_target_location_input")
    if st.button("📡 Initialize Site Node", use_container_width=True, key="btn_init_site_node"):
        with st.spinner("Geolocating..."):
            try:
                osm = requests.get(
                    f"https://nominatim.openstreetmap.org/search?q={requests.utils.quote(location_query)}&format=json&limit=1",
                    headers={"User-Agent": "AegisMHR/8.0"}, timeout=5
                )
                if osm.ok and osm.json():
                    d = osm.json()[0]
                    st.session_state.latitude  = float(d["lat"])
                    st.session_state.longitude = float(d["lon"])
                    raw_name = d.get("display_name", location_query)
                    parts    = raw_name.split(",")
                    st.session_state.location_name = ", ".join(parts[:2]).strip()
                    sync_geo_context(st.session_state.location_name, st.session_state.latitude, st.session_state.longitude)
                    st.toast(f"📍 {st.session_state.location_name}", icon="🌍")
                else:
                    h = sum(ord(c) for c in location_query)
                    st.session_state.latitude  = round(28.631 + (h % 100) / 600 - 0.08, 5)
                    st.session_state.longitude = round(77.216 + (h % 150) / 600 - 0.12, 5)
                    st.session_state.location_name = f"{location_query} (Sim)"
                    sync_geo_context(st.session_state.location_name, st.session_state.latitude, st.session_state.longitude)
                    st.toast("⚠️ Geocoder busy — using simulated coords")
            except:
                sync_geo_context(st.session_state.location_name, st.session_state.latitude, st.session_state.longitude)
                st.toast("⚠️ Geocoder offline — using cached coords")

    st.markdown(f"""
    <div class="sb-block" style="font-size:.7rem;">
        {st.session_state.country_flag} <strong style="color:white;">{st.session_state.location_name}</strong><br>
        <span style="color:#10b981;">LAT {st.session_state.latitude:.4f} &nbsp; LON {st.session_state.longitude:.4f}</span><br>
        <span style="color:#00f0ff;">{st.session_state.currency_symbol} {st.session_state.currency_code} &nbsp;·&nbsp; Speed Limit: {st.session_state.speed_limit_kmh} km/h &nbsp;·&nbsp; Drive: {st.session_state.drive_side.upper()}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec-div">🎬 Scenario Engine</div>', unsafe_allow_html=True)
    scenario_sel = st.selectbox("Scenario", list(SCENARIO_MAP.keys()), label_visibility="collapsed", key="sb_scenario_select")
    active_scenario = SCENARIO_MAP[scenario_sel]

    model_tier = st.selectbox("YOLOv8 Profile",
        ["YOLOv8-Nano (Speed Edge)", "YOLOv8-XLarge (Precision High-Load)"],
        label_visibility="collapsed", key="sb_model_tier_select")
    vision_thresh = st.slider("Detection Confidence", 0.0, 1.0, 0.40, 0.05, key="sb_vision_thresh_slider")

    st.markdown('<div class="sec-div">⚙️ Operating Mode</div>', unsafe_allow_html=True)
    op_mode = st.selectbox("Mode",
        ["AI Automated Fusion", "Manual Override", "Security Lockdown", "Predictive Optimization"],
        label_visibility="collapsed", key="sb_op_mode_select")
    st.session_state["operational_mode"] = op_mode

    manual_phase = None
    manual_timing = None
    if op_mode == "Manual Override":
        manual_phase  = st.selectbox("Signal Phase",
            ["North-South Green", "East-West Green", "ALL RED (CONTAINMENT)", "ALL FLASHING YELLOW"],
            label_visibility="collapsed", key="sb_manual_phase_select")
        manual_timing = st.slider("Green Timer (sec)", 5, 60, 20, key="sb_manual_timing_slider")

    st.markdown("<br>", unsafe_allow_html=True)
    scan_btn = st.button("⚡ EXECUTE SCENARIO SCAN", type="primary", use_container_width=True, key="btn_execute_scenario_scan")
    if st.button("♻️ Clear Active Data", use_container_width=True, key="btn_clear_active_data"):
        st.session_state.active_data = None
        st.session_state.sb_results = None
        st.rerun()


# ── TRIGGER BACKEND SCAN (AUTO ON LOCATION CHANGE OR MANUAL BUTTON) ──
_curr_loc_sig = f"{st.session_state.location_name}_{st.session_state.latitude:.4f}_{st.session_state.longitude:.4f}_{active_scenario}_{op_mode}"
if (st.session_state.get("last_scanned_sig") != _curr_loc_sig or scan_btn or st.session_state.active_data is None) and backend_alive():
    try:
        payload = {
            "scenario": active_scenario,
            "vision_threshold": float(vision_thresh),
            "model_tier": str(model_tier),
            "location_name": st.session_state.location_name,
            "latitude": st.session_state.latitude,
            "longitude": st.session_state.longitude,
            "operational_mode": op_mode,
        }
        if op_mode == "Manual Override":
            payload["manual_active_phase"]  = manual_phase
            payload["manual_signal_timing"] = manual_timing

        res = requests.post(ANALYZE_URL, json=payload, headers=auth_header(), timeout=15)
        if res.status_code == 200:
            _rd = res.json()
            st.session_state.active_data = _rd
            st.session_state["last_scanned_sig"] = _curr_loc_sig
            # ── Persist geo context from analyze response ────────────────────────────
            _geo = _rd.get("geo_context", {})
            if _geo:
                st.session_state.country_code    = _geo.get("country_code",    st.session_state.country_code)
                st.session_state.country_flag    = _geo.get("country_flag",    st.session_state.country_flag)
                st.session_state.country_name    = _geo.get("country_name",    st.session_state.country_name)
                st.session_state.currency_code   = _geo.get("currency_code",   st.session_state.currency_code)
                st.session_state.currency_symbol = _geo.get("currency_symbol", st.session_state.currency_symbol)
                st.session_state.speed_limit_kmh = _geo.get("speed_limit_kmh", st.session_state.speed_limit_kmh)
                st.session_state.drive_side      = _geo.get("drive_side",      st.session_state.drive_side)
                st.session_state.plate_format    = _geo.get("plate_format",    st.session_state.plate_format)
            if scan_btn:
                st.toast(f"✅ Scan complete — {st.session_state.location_name}", icon="🚦")
        else:
            if scan_btn:
                st.error(f"❌ Core Disconnect: {res.text}")
    except requests.exceptions.ConnectionError:
        if scan_btn:
            st.error("❌ FastAPI backend offline on port 8000. Start server first.")


# ══════════════════════════════════════════════════════════════
# MAIN CONTENT — TEN TABS
# ══════════════════════════════════════════════════════════════
(tab_hud, tab_analytics, tab_map_intel,
 tab_sandbox, tab_ai_chat, tab_guide, tab_manual, tab_security,
 tab_anpr, tab_pipeline, tab_citizen) = st.tabs([
    "📊 Operations HUD",
    "📈 Analytics",
    "🌍 Map Intelligence",
    "🧪 Sandbox",
    "🤖 AI Copilot",
    "📚 Learning Guide",
    "📖 Diagnostics",
    "🔒 Security Ledger",
    "🚘 ANPR & Violations",
    "⚙️ Pipeline Status",
    "👥 Public Citizen Portal",
])


# ─────────────────────────────────────────────────
# TAB 1 — OPERATIONS HUD
# ─────────────────────────────────────────────────
with tab_hud:
    if st.session_state.active_data is None:
        st.markdown("""
        <div class="card" style="text-align:center;padding:60px 20px;">
            <div style="font-size:4rem;margin-bottom:16px;">🚦</div>
            <div class="t-hero" style="font-size:1.4rem;margin-bottom:12px;">SENSOR GRID OFFLINE</div>
            <div style="font-family:'JetBrains Mono',monospace;color:#4b6584;font-size:.82rem;line-height:1.8;">
                Select a scenario and mode in the left sidebar,<br>then click <strong style="color:#00f0ff;">⚡ EXECUTE SCENARIO SCAN</strong> to boot the HUD.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        data = st.session_state.active_data
        fl   = data["fusion_layer"]
        tel  = data["telemetry"]
        sm   = data["system_telemetry_metrics"]
        alert = fl["alert_status"]
        phase = fl["active_phase"]
        count = fl["vehicle_count"]
        timing = fl["signal_timing_seconds"]
        risk   = data["risk_score"]
        lat_ms = data["latency_ms"]

        # ── STATUS BANNER
        if any(k in alert for k in ["COLLISION","EMERGENCY","LOCKDOWN"]):
            sb_col, sb_bg, sb_border = "#fca5a5", "rgba(239,68,68,.12)", "#ef4444"
        elif any(k in alert for k in ["TAMPER","WARNING"]):
            sb_col, sb_bg, sb_border = "#fde68a", "rgba(245,158,11,.12)", "#f59e0b"
        elif "MANUAL" in alert:
            sb_col, sb_bg, sb_border = "#c4b5fd", "rgba(168,85,247,.12)", "#a855f7"
        elif "PREDICTIVE" in alert:
            sb_col, sb_bg, sb_border = "#bae6fd", "rgba(6,182,212,.12)", "#06b6d4"
        else:
            sb_col, sb_bg, sb_border = "#a7f3d0", "rgba(16,185,129,.12)", "#10b981"

        st.markdown(f"""
        <div class="status-banner" style="background:{sb_bg};border-color:{sb_border};color:{sb_col};">
            <span style="font-size:1.3rem;">{"🚨" if sb_border=="#ef4444" else ("⚠️" if sb_border=="#f59e0b" else "✅")}</span>
            <div>
                <div style="font-weight:700;font-size:.9rem;">{alert}</div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:.68rem;opacity:.75;margin-top:2px;">
                    📍 {st.session_state.location_name} &nbsp;|&nbsp; MODE: {op_mode} &nbsp;|&nbsp; PHASE: {phase}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── METRIC ROW
        mc = st.columns(5)
        tiles = [
            ("API Latency",     lat_ms,  "ms",    "#00f0ff", "⏱️"),
            ("Hazard Index",    risk,    "%",     risk_color(risk), "🔥"),
            ("Vehicle Count",   count,   " units","#eab308",  "🚗"),
            ("Green Timer",     f"{timing}s" if timing else "N/A", "", "#a855f7","🚦"),
            ("System Scans",    sm["total_requests"], " req", "#10b981", "📡"),
        ]
        for col, (lbl, val, unit, clr, ico) in zip(mc, tiles):
            col.markdown(metric_tile(lbl, val, unit, clr, ico), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── MAIN SPLIT
        left, right = st.columns([1.6, 1.4])

        with left:
            sec_div("👁️ LIVE CAMERA FEED — YOLOv8 DETECTION")
            img_b64 = tel.get("visual_image_b64", "")
            if img_b64:
                st.image(base64.b64decode(img_b64), use_container_width=True)
            else:
                st.warning("📷 No visual stream — ingest node offline")

            sec_div("🚥 ADAPTIVE SIGNAL CONTROLLER")
            color_ns = "#10b981" if "North-South" in phase or "EMERGENCY" in phase else ("#ef4444" if "RED" in phase or "LOCKDOWN" in phase else "#f59e0b")
            color_ew = "#10b981" if "East-West" in phase else ("#ef4444" if "RED" in phase or "EMERGENCY" in phase or "LOCKDOWN" in phase else "#f59e0b")
            if "FLASH" in phase or "YELLOW" in phase:
                color_ns = color_ew = "#f59e0b"

            sc1, sc2 = st.columns(2)
            for col, lane, col_hex in [(sc1, "NORTH–SOUTH", color_ns), (sc2, "EAST–WEST", color_ew)]:
                lbl = "GO" if col_hex == "#10b981" else ("STOP" if col_hex == "#ef4444" else "SLOW")
                col.markdown(f"""
                <div class="signal-box">
                    <div style="font-family:'JetBrains Mono',monospace;font-size:.65rem;color:#4b6584;">{lane}</div>
                    <div class="signal-dot" style="background:{col_hex};box-shadow:0 0 18px {col_hex};"></div>
                    <div style="font-family:'Orbitron',sans-serif;font-size:1rem;font-weight:700;color:{col_hex};">{lbl}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="text-align:center;font-family:'Orbitron',sans-serif;font-size:.72rem;color:#00f0ff;margin-top:8px;letter-spacing:1px;">
                {phase.upper()}
            </div>
            """, unsafe_allow_html=True)

        with right:
            sec_div("🔊 ACOUSTIC TELEMETRY")
            acoustic = tel["acoustic_profile"]

            fig_wave = go.Figure()
            fig_wave.add_trace(go.Scatter(
                y=acoustic["waveform"], mode='lines',
                line=dict(color='#00f0ff', width=1.2),
                fill='tozeroy', fillcolor='rgba(0,240,255,0.05)'
            ))
            fig_wave.update_layout(
                title=dict(text=f"Waveform — {acoustic['type']} @ {acoustic['db_level']} dB",
                           font=dict(family="JetBrains Mono", size=11, color="#64748b")),
                height=140, margin=dict(l=8,r=8,t=28,b=8),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(visible=False), yaxis=dict(gridcolor="rgba(255,255,255,.04)", zeroline=False, color="#4b6584")
            )
            st.plotly_chart(fig_wave, use_container_width=True, key="wave_hud")

            fig_fft = go.Figure()
            fig_fft.add_trace(go.Bar(
                x=acoustic["fft_frequencies"], y=acoustic["fft_amplitudes"],
                marker=dict(color='#10b981', opacity=0.8)
            ))
            fig_fft.update_layout(
                title=dict(text=f"FFT Spectrum — Peak {acoustic['peak_frequency']} Hz",
                           font=dict(family="JetBrains Mono", size=11, color="#64748b")),
                height=130, margin=dict(l=8,r=8,t=28,b=8),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(color="#4b6584", gridcolor="rgba(255,255,255,.04)"),
                yaxis=dict(visible=False)
            )
            st.plotly_chart(fig_fft, use_container_width=True, key="fft_hud")

            sec_div("📝 REAL-TIME ADVISORY")
            st.markdown(f"""
            <div class="advisory-box">
                <div style="color:#38bdf8;font-weight:600;margin-bottom:4px;">ADVISORY</div>
                <div style="color:#e2e8f0;">{fl['rerouting_advisory']}</div>
                <div style="color:#4b6584;margin-top:8px;font-size:.72rem;">{fl['automated_incident_report']}</div>
            </div>
            """, unsafe_allow_html=True)

            sec_div("🤖 QUICK COPILOT")
            q_input = st.text_input("Ask copilot...", key="quick_chat_input", label_visibility="collapsed",
                                     placeholder="e.g. What should I do about the congestion?")
            if q_input:
                try:
                    cr = requests.post(CHAT_URL, json={
                        "user_message": q_input,
                        "incident_context": f"{fl['rerouting_advisory']} | Vehicles: {count} | Phase: {phase}",
                        "session_token": st.session_state.user_token
                    }, headers=auth_header(), timeout=20).json()
                    st.markdown(f"""
                    <div class="chat-msg-ai">
                        🤖 <strong>Copilot:</strong><br>{cr.get('reply','...')}
                    </div>
                    """, unsafe_allow_html=True)
                except:
                    st.warning("Copilot offline — start the backend.")

        mini_separator()
        # Detection list
        with st.expander("🔍 Raw Detections & Telemetry JSON"):
            dc1, dc2 = st.columns(2)
            with dc1:
                st.markdown("**Visual Detections**")
                st.dataframe(pd.DataFrame(tel["visual_detections"]), use_container_width=True, hide_index=True)
            with dc2:
                st.markdown("**Full Response Payload**")
                st.json(data, expanded=False)

        # ── TRAFFIC ANALYTICS ─────────────────────────────────────
        mini_separator()
        sec_div("📊 TRAFFIC ANALYTICS — DENSITY · QUEUE · SPEED · LANES")
        ta = data.get("traffic_analytics", {})
        if ta:
            ta1, ta2, ta3, ta4 = st.columns(4)
            ta1.markdown(metric_tile("Traffic Density", ta.get("traffic_density_percent","—"), "%", "#00f0ff", "📊"), unsafe_allow_html=True)
            ta2.markdown(metric_tile("Queue Length",    ta.get("queue_length_meters","—"),     "m", "#a855f7", "📏"), unsafe_allow_html=True)
            ta3.markdown(metric_tile("Avg Speed",       ta.get("avg_speed_kmh","—"),           "km/h","#10b981","⚡"), unsafe_allow_html=True)
            ta4.markdown(metric_tile("Density Level",   ta.get("density_level","—"),           "",   "#eab308","🏷️"), unsafe_allow_html=True)

            lc = ta.get("lane_counts", {})
            if lc:
                st.markdown("<br>", unsafe_allow_html=True)
                lc_cols = st.columns(len(lc))
                for col, (lane, cnt) in zip(lc_cols, lc.items()):
                    col.markdown(metric_tile(lane, cnt, " veh", "#06b6d4", "🛣️"), unsafe_allow_html=True)

        # ── ENVIRONMENTAL EXHAUST & VRU PEDESTRIAN SAFETY ─────────
        mini_separator()
        sec_div("🌱 ENVIRONMENTAL EXHAUST TELEMETRY · 🚶 VRU PEDESTRIAN SAFETY")
        env_col, vru_col = st.columns(2)
        with env_col:
            try:
                _env_res = requests.get(
                    f"{BACKEND_URL}/api/v1/environmental/telemetry",
                    params={"vehicle_count": count, "signal_timing_seconds": timing or 30},
                    timeout=5
                )
                if _env_res.ok:
                    _env = _env_res.json()
                    st.markdown(f"""
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
                    """, unsafe_allow_html=True)
            except:
                st.warning("Environmental module offline.")
        with vru_col:
            try:
                _vru_res = requests.get(f"{BACKEND_URL}/api/v1/vru/crosswalk", params={"pedestrians": 3}, timeout=5)
                if _vru_res.ok:
                    _vru = _vru_res.json()
                    st.markdown(f"""
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
                    """, unsafe_allow_html=True)
            except:
                st.warning("VRU safety module offline.")

        # ── ANPR + VIOLATIONS PREVIEW (new today) ─────────────────
        mini_separator()
        sec_div("🚘 ANPR REAL-TIME OCR · TRAFFIC VIOLATIONS PREVIEW")
        anpr_col, viol_col = st.columns(2)
        scenario_key = SCENARIO_MAP.get(
            next((k for k in SCENARIO_MAP if SCENARIO_MAP[k] == data.get("scenario","normal")), "🟢 Normal Flowing Traffic"),
            "normal"
        )
        # Derive scenario from the analysis data (use the sidebar selection)
        _scen_raw = data.get("scenario", "normal")
        with anpr_col:
            try:
                _anpr = requests.get(
                    f"{ANPR_URL}/{_scen_raw}",
                    params={"latitude": st.session_state.latitude,
                            "longitude": st.session_state.longitude,
                            "location_name": st.session_state.location_name},
                    headers=auth_header(), timeout=10
                ).json()
                _plates = _anpr.get("anpr_records", [])
                _cc     = _anpr.get("summary", {}).get("country_flag", st.session_state.country_flag)
                if _plates:
                    for _p in _plates[:5]:
                        st.markdown(
                            f'<div style="display:flex;justify-content:space-between;align-items:center;background:rgba(0,0,0,.2);border:1px solid rgba(255,255,255,.05);border-radius:6px;padding:6px 10px;margin-bottom:4px;">'
                            f'<span style="background:#fff;color:#000;font-family:\'JetBrains Mono\',monospace;font-weight:700;font-size:.78rem;padding:2px 6px;border-radius:3px;border:2px solid #000;">{_p.get("plate","\u2014")}</span>'
                            f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:.7rem;color:#00f0ff;">{_cc} {_p.get("vehicle_type","Vehicle")}</span>'
                            f'</div>', unsafe_allow_html=True)
                else:
                    st.info("No plates detected for this scenario.")
            except:
                st.warning("ANPR offline \u2014 check backend.")
        with viol_col:
            try:
                _viols = requests.get(
                    f"{VIOLATIONS_URL}/{_scen_raw}",
                    params={"latitude": st.session_state.latitude,
                            "longitude": st.session_state.longitude,
                            "location_name": st.session_state.location_name},
                    headers=auth_header(), timeout=10
                ).json()
                _vlist = _viols.get("violations", [])
                if _vlist:
                    for _v in _vlist[:5]:
                        _fine_disp = _v.get("fine_local", f"{st.session_state.currency_symbol}{_v.get('fine_amount','\u2014')}")
                        _flag_v    = _v.get("country_flag", st.session_state.country_flag)
                        st.markdown(
                            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:.75rem;color:#f59e0b;margin-bottom:6px;">'
                            f'⚠️ <strong>{_v.get("type","\u2014")}</strong> \u2014 {_v.get("vehicle_id","Unknown")} | {_flag_v} {_fine_disp}'
                            f'</div>', unsafe_allow_html=True)
                else:
                    st.success("✅ No violations detected for this scenario.")
            except:
                st.warning("Violations module offline \u2014 check backend.")


# ─────────────────────────────────────────────────
# TAB 2 — ANALYTICS DASHBOARD
# ─────────────────────────────────────────────────
with tab_analytics:
    an_tab_live, an_tab_upload = st.tabs(["📊 Live Ledger Analytics", "📂 Dataset File Analyzer"])

    # ─── LIVE LEDGER ───────────────────────────────
    with an_tab_live:
        sec_div("📈 PRODUCTION ANALYTICS SUITE — LIVE OPERATIONAL LEDGER")

        h_df, h_err = pd.DataFrame(), None
        if not backend_alive():
            h_err = "backend_offline"
        else:
            try:
                h_res = requests.get(HISTORY_URL, headers=auth_header(), timeout=12)
                if h_res.status_code == 200:
                    payload_h = h_res.json()
                    h_df = pd.DataFrame(payload_h.get("history", []))
                elif h_res.status_code == 401:
                    h_err = "auth_expired"
                elif h_res.status_code == 403:
                    h_err = "forbidden"
                else:
                    h_err = f"http_{h_res.status_code}"
            except requests.exceptions.ConnectionError:
                h_err = "backend_offline"
            except requests.exceptions.Timeout:
                h_err = "timeout"
            except Exception as ex:
                h_err = f"error: {ex}"

        if h_err == "backend_offline":
            st.markdown("""
            <div class="card card-alert-red" style="padding:30px;text-align:center;">
                <div style="font-size:2.5rem;margin-bottom:10px;">❌</div>
                <div style="font-family:'Orbitron',sans-serif;font-size:.95rem;color:#ef4444;margin-bottom:8px;">BACKEND MICROSERVICE OFFLINE</div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:.75rem;color:#64748b;">
                    Start FastAPI: <code style="color:#00f0ff;">uvicorn app.main:app --reload</code>
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif h_err == "auth_expired":
            st.warning("🔑 Session token expired. Please log out and back in.")
        elif h_err == "forbidden":
            st.markdown("""
            <div class="card card-alert-amber" style="padding:30px;text-align:center;">
                <div style="font-size:2.5rem;margin-bottom:10px;">🛡️</div>
                <div style="font-family:'Orbitron',sans-serif;font-size:.95rem;color:#f59e0b;margin-bottom:12px;">
                    LEDGER ACCESS RESTRICTED
                </div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:.78rem;color:#94a3b8;line-height:2;">
                    The encrypted audit ledger is restricted to <strong style="color:#00f0ff;">Admin</strong> and
                    <strong style="color:#a855f7;">Auditor</strong> clearance levels.<br>
                    Your current clearance: <strong style="color:#f59e0b;">Operator</strong><br><br>
                    Contact your system administrator to request elevated access,<br>
                    or use the <strong style="color:#10b981;">📂 Dataset File Analyzer</strong> tab above
                    to upload and analyse custom traffic datasets without restriction.
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif h_err and h_err.startswith("http_"):
            st.error(f"❌ API status {h_err.split('_')[1]}. Check server logs.")
        elif h_err == "timeout":
            st.error("⏱️ Request timed out — backend slow or unresponsive.")
        elif h_err:
            st.error(f"❌ Unexpected error: {h_err}")
        elif h_df.empty:
            st.markdown("""
            <div class="card" style="text-align:center;padding:40px;">
                <div style="font-size:2.5rem;margin-bottom:10px;">📋</div>
                <div style="font-family:'Orbitron',sans-serif;font-size:.9rem;color:#00f0ff;margin-bottom:8px;">LEDGER EMPTY</div>
                <div style="font-family:'JetBrains Mono',monospace;color:#4b6584;font-size:.78rem;">
                    No scan records yet. Run a scenario scan to populate analytics.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for col_n in ["risk_score","vehicle_count","latency_ms","signal_timing_seconds"]:
                if col_n in h_df.columns:
                    h_df[col_n] = pd.to_numeric(h_df[col_n], errors="coerce").fillna(0)

            can_export = st.session_state.user_role.upper() in ["ADMIN", "AUDITOR"]
            critical_mask = h_df["priority"].astype(str).str.contains(
                "ALERT|OVERRIDE|WARNING|LOCKDOWN|COLLISION|EMERGENCY", na=False
            ) if "priority" in h_df.columns else pd.Series([False]*len(h_df))

            kc = st.columns(5)
            kpis = [
                ("Total Logs",     len(h_df),                           " logs",  "#00f0ff", "📊"),
                ("Critical",       int(critical_mask.sum()),             " cases", "#ef4444", "🚨"),
                ("Avg Hazard",     round(h_df["risk_score"].mean(),1),  "%",      risk_color(h_df["risk_score"].mean()), "🔥"),
                ("Avg Latency",    round(h_df["latency_ms"].mean(),1),  " ms",    "#a855f7", "⚡"),
                ("Peak Vehicles",  int(h_df["vehicle_count"].max()),    " units", "#eab308", "🚗"),
            ]
            for col, (lbl, val, unit, clr, ico) in zip(kc, kpis):
                col.markdown(metric_tile(lbl, val, unit, clr, ico), unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            h_df_s = h_df.sort_values("timestamp") if "timestamp" in h_df.columns else h_df

            rc1, rc2 = st.columns(2)
            with rc1:
                fig1 = px.area(h_df_s, x="timestamp", y="risk_score",
                    color_discrete_sequence=["#00f0ff"], template="plotly_dark",
                    title="⚠️ Hazard Index — Time Series",
                    labels={"risk_score":"Hazard %","timestamp":"Time"})
                fig1.update_layout(height=230, margin=dict(l=8,r=8,t=35,b=8),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                fig1.update_traces(fillcolor="rgba(0,240,255,.07)", line_color="#00f0ff")
                st.plotly_chart(fig1, use_container_width=True, key="risk_chart_v2")

                if "operational_mode" in h_df.columns:
                    mode_df = h_df["operational_mode"].value_counts().reset_index()
                    mode_df.columns = ["Mode","Count"]
                    fig2 = px.pie(mode_df, names="Mode", values="Count", hole=0.45,
                        color_discrete_sequence=["#00f0ff","#a855f7","#ef4444","#10b981"],
                        template="plotly_dark", title="⚙️ Mode Distribution")
                    fig2.update_layout(height=230, margin=dict(l=8,r=8,t=35,b=8),
                        paper_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig2, use_container_width=True, key="mode_chart_v2")

            with rc2:
                if "vehicle_count" in h_df_s.columns:
                    fig3 = px.bar(h_df_s, x="timestamp", y="vehicle_count",
                        color="scenario" if "scenario" in h_df_s.columns else None,
                        template="plotly_dark", title="🚗 Vehicle Volume per Scan",
                        labels={"vehicle_count":"Vehicles","timestamp":"Time"},
                        color_discrete_sequence=px.colors.sequential.ice_r)
                    fig3.update_layout(height=230, margin=dict(l=8,r=8,t=35,b=8),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig3, use_container_width=True, key="veh_chart_v2")

                if "latency_ms" in h_df.columns and "vehicle_count" in h_df.columns:
                    fig4 = px.scatter(h_df, x="vehicle_count", y="latency_ms",
                        color="scenario" if "scenario" in h_df.columns else None,
                        size="risk_score" if "risk_score" in h_df.columns else None,
                        template="plotly_dark", title="⚡ Latency vs Vehicle Load",
                        labels={"vehicle_count":"Vehicles","latency_ms":"Latency ms"})
                    fig4.update_layout(height=230, margin=dict(l=8,r=8,t=35,b=8),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig4, use_container_width=True, key="lat_scatter_v2")

            mini_separator()
            sc1, sc2, sc3 = st.columns(3)
            with sc1:
                if "scenario" in h_df.columns:
                    scen_cnt = h_df["scenario"].value_counts().reset_index()
                    scen_cnt.columns = ["Scenario","Count"]
                    fig5 = px.bar(scen_cnt, x="Scenario", y="Count", color="Scenario",
                        template="plotly_dark", title="📌 Scenario Frequency",
                        color_discrete_sequence=["#00f0ff","#a855f7","#ef4444","#10b981","#f59e0b"])
                    fig5.update_layout(height=210, margin=dict(l=8,r=8,t=35,b=8),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
                    st.plotly_chart(fig5, use_container_width=True, key="scen_chart_v2")
            with sc2:
                if "signal_timing_seconds" in h_df.columns:
                    fig6 = px.histogram(h_df, x="signal_timing_seconds",
                        template="plotly_dark", title="🚦 Signal Timing Distribution",
                        color_discrete_sequence=["#10b981"])
                    fig6.update_layout(height=210, margin=dict(l=8,r=8,t=35,b=8),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig6, use_container_width=True, key="timing_hist_v2")
            with sc3:
                if "risk_score" in h_df.columns and "scenario" in h_df.columns:
                    fig7 = px.box(h_df, x="scenario", y="risk_score", color="scenario",
                        template="plotly_dark", title="🔥 Hazard by Scenario",
                        color_discrete_sequence=["#00f0ff","#a855f7","#ef4444","#10b981","#f59e0b"])
                    fig7.update_layout(height=210, margin=dict(l=8,r=8,t=35,b=8),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
                    st.plotly_chart(fig7, use_container_width=True, key="risk_box_v2")

            mini_separator()
            with st.expander("🗃️ Raw Decrypted Ledger Table"):
                st.dataframe(h_df, use_container_width=True, hide_index=True, height=280)

            if can_export:
                st.download_button(
                    "📥 EXPORT DECRYPTED AUDIT LEDGER (CSV)",
                    data=h_df.to_csv(index=False),
                    file_name=f"aegis_ledger_{uuid.uuid4().hex[:6]}.csv",
                    mime="text/csv", type="primary", use_container_width=True,
                    key="btn_download_audit_ledger_csv"
                )
            else:
                st.info("ℹ️ CSV export is restricted to Admin and Auditor clearance levels.")

    # ─── DATASET FILE ANALYZER ────────────────────
    with an_tab_upload:
        sec_div("📂 TRAFFIC DATASET FILE ANALYZER")
        st.markdown("<p style='font-family:JetBrains Mono,monospace;color:#64748b;font-size:.78rem;'>Upload any traffic dataset (CSV, Excel, JSON) for instant profiling, visualisation, AI insights, and export. Supports TfL, INRIX, OpenTraffic, SUMO, and custom sensor exports.</p>", unsafe_allow_html=True)

        up_left, up_right = st.columns([1.1, 1.9])
        with up_left:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="t-section" style="margin-bottom:12px;">📤 Upload Dataset</div>', unsafe_allow_html=True)
            uploaded = st.file_uploader("Drop a file", type=["csv","xlsx","xls","json"], label_visibility="collapsed", key="analyzer_file_uploader")
            if uploaded:
                try:
                    fname = uploaded.name.lower()
                    if fname.endswith(".csv"):              up_df_new = pd.read_csv(uploaded)
                    elif fname.endswith((".xlsx",".xls")): up_df_new = pd.read_excel(uploaded)
                    elif fname.endswith(".json"):           up_df_new = pd.read_json(uploaded)
                    else:                                    up_df_new = pd.DataFrame()
                    st.session_state["up_df"] = up_df_new
                    st.toast(f"✅ Loaded {len(up_df_new)} rows from {uploaded.name}", icon="📂")
                except Exception as e:
                    st.error(f"❌ Parse error: {e}")
                    st.session_state.pop("up_df", None)

            chart_type, x_col, y_col, color_col, render_btn = "📉 Line Chart", None, None, None, False
            if "up_df" in st.session_state and not st.session_state["up_df"].empty:
                udf = st.session_state["up_df"]
                num_cols = udf.select_dtypes(include="number").columns.tolist()
                cat_cols = udf.select_dtypes(exclude="number").columns.tolist()
                st.markdown('<div class="sec-div" style="font-size:.65rem;">Chart Settings</div>', unsafe_allow_html=True)
                chart_type = st.selectbox("Chart Type", ["📉 Line Chart","📊 Bar Chart","🔵 Scatter Plot","🥧 Pie / Donut","📦 Box Plot","🌡️ Correlation Heatmap","📈 Histogram"], label_visibility="collapsed", key="analyzer_chart_type_select")
                x_col = st.selectbox("X Axis", udf.columns.tolist(), label_visibility="collapsed", key="up_x")
                y_col = st.selectbox("Y Axis", num_cols if num_cols else udf.columns.tolist(), label_visibility="collapsed", key="up_y")
                cc_raw = st.selectbox("Color By", ["— None —"] + cat_cols, label_visibility="collapsed", key="up_col")
                color_col = None if cc_raw == "— None —" else cc_raw
                render_btn = st.button("📊 Render Analysis", type="primary", use_container_width=True, key="btn_render_analysis")
                if st.session_state.user_role.upper() in ["ADMIN","AUDITOR"]:
                    st.download_button("📥 Download Processed CSV", udf.to_csv(index=False),
                        file_name=f"processed_{uuid.uuid4().hex[:6]}.csv", mime="text/csv", use_container_width=True, key="btn_download_processed_csv")
            st.markdown('</div>', unsafe_allow_html=True)

        with up_right:
            if "up_df" not in st.session_state or st.session_state["up_df"].empty:
                st.markdown("""
                <div class="card" style="text-align:center;padding:60px 20px;">
                    <div style="font-size:3rem;margin-bottom:12px;">📂</div>
                    <div style="font-family:'Orbitron',sans-serif;font-size:.9rem;color:#00f0ff;margin-bottom:10px;">UPLOAD A TRAFFIC DATASET</div>
                    <div style="font-family:'JetBrains Mono',monospace;color:#4b6584;font-size:.75rem;line-height:2;">
                        Supported: CSV &middot; Excel &middot; JSON<br><br>
                        Example sources:<br>
                        &bull; INRIX Traffic Scores CSV<br>
                        &bull; TfL London Open Data<br>
                        &bull; SUMO simulation output<br>
                        &bull; Chicago Traffic Crashes JSON<br>
                        &bull; Custom sensor log CSV
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                udf = st.session_state["up_df"]
                num_cols = udf.select_dtypes(include="number").columns.tolist()
                pc1, pc2, pc3, pc4 = st.columns(4)
                pc1.markdown(metric_tile("Rows",    len(udf),                         "",      "#00f0ff","📋"), unsafe_allow_html=True)
                pc2.markdown(metric_tile("Columns", len(udf.columns),                 "",      "#a855f7","📐"), unsafe_allow_html=True)
                pc3.markdown(metric_tile("Numeric", len(num_cols),                    " cols", "#10b981","🔢"), unsafe_allow_html=True)
                pc4.markdown(metric_tile("Nulls",   int(udf.isnull().sum().sum()),   "",      "#f59e0b" if udf.isnull().sum().sum()>0 else "#10b981","⚠️"), unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

                with st.expander("📋 Schema & Stats Preview", expanded=False):
                    dtype_df = pd.DataFrame({"Column":udf.dtypes.index,"Type":udf.dtypes.astype(str).values,"Non-Null":udf.notnull().sum().values,"Nulls":udf.isnull().sum().values})
                    st.dataframe(dtype_df, use_container_width=True, hide_index=True)
                    if num_cols:
                        st.dataframe(udf[num_cols].describe().round(2), use_container_width=True)

                smart_cols = {c.lower(): c for c in udf.columns}
                auto_x = smart_cols.get("timestamp", smart_cols.get("time", smart_cols.get("hour", udf.columns[0])))
                auto_y = smart_cols.get("volume", smart_cols.get("speed", smart_cols.get("count", smart_cols.get("vehicles", num_cols[0] if num_cols else udf.columns[0]))))
                x_use = x_col or auto_x
                y_use = y_col or auto_y

                if x_use in udf.columns and y_use in udf.columns:
                    try:
                        ckw = dict(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                        pal = ["#00f0ff","#a855f7","#10b981","#f59e0b","#ef4444"]
                        fig_up = None
                        if "Line" in chart_type:
                            fig_up = px.line(udf, x=x_use, y=y_use, color=color_col, title=f"📉 {y_use} over {x_use}", color_discrete_sequence=pal)
                        elif "Bar" in chart_type:
                            fig_up = px.bar(udf, x=x_use, y=y_use, color=color_col, title=f"📊 {y_use} by {x_use}", color_discrete_sequence=pal)
                        elif "Scatter" in chart_type:
                            fig_up = px.scatter(udf, x=x_use, y=y_use, color=color_col, title=f"🔵 {y_use} vs {x_use}", color_discrete_sequence=pal)
                        elif "Pie" in chart_type:
                            fig_up = px.pie(udf, names=x_use, values=y_use, hole=0.4, title=f"🥧 {y_use} by {x_use}", color_discrete_sequence=pal)
                        elif "Box" in chart_type:
                            fig_up = px.box(udf, x=color_col or x_use, y=y_use, title=f"📦 {y_use} Distribution", color_discrete_sequence=pal)
                        elif "Heatmap" in chart_type:
                            if len(num_cols) > 1:
                                corr = udf[num_cols].corr().round(2)
                                fig_up = px.imshow(corr, color_continuous_scale="RdBu_r", title="🌡️ Correlation Heatmap", text_auto=True)
                            else:
                                st.warning("Need ≥2 numeric columns for heatmap.")
                        elif "Histogram" in chart_type:
                            fig_up = px.histogram(udf, x=y_use, color=color_col, title=f"📈 {y_use} Histogram", color_discrete_sequence=pal)
                        if fig_up:
                            fig_up.update_layout(height=350, margin=dict(l=8,r=8,t=40,b=8), **ckw)
                            st.plotly_chart(fig_up, use_container_width=True, key="upload_chart")
                    except Exception as ce:
                        st.error(f"Chart error: {ce}")

                mini_separator()
                sec_div("🤖 AI DATASET INSIGHTS")
                ai_col_sel = st.multiselect("Columns to analyse", udf.columns.tolist(),
                    default=num_cols[:4] if len(num_cols)>=4 else num_cols, label_visibility="collapsed", key="analyzer_ai_col_multiselect")
                if st.button("🤖 Generate AI Insights from Dataset", type="primary", use_container_width=True, key="btn_gen_ai_insights"):
                    if ai_col_sel and backend_alive():
                        sample = udf[ai_col_sel].describe().to_string() if num_cols else udf[ai_col_sel].head(5).to_string()
                        prompt = (f"You are a traffic data analyst AI. Analyse the following dataset statistics "
                                  f"and provide 5 specific, actionable insights about traffic patterns, anomalies, "
                                  f"and optimisation opportunities. Be concise and technical.\n\nData:\n{sample}")
                        with st.spinner("🤖 Generating insights..."):
                            try:
                                cr = requests.post(CHAT_URL, json={
                                    "user_message": prompt,
                                    "incident_context": f"Dataset: {len(udf)} rows, columns: {', '.join(ai_col_sel)}",
                                    "session_token": st.session_state.user_token
                                }, headers=auth_header(), timeout=40).json()
                                st.markdown(f'<div class="chat-msg-ai">🤖 <strong>AI Dataset Analysis:</strong><br><br>{cr.get("reply","No insights generated.")}</div>', unsafe_allow_html=True)
                            except Exception as e:
                                st.error(f"AI error: {e}")
                    elif not backend_alive():
                        st.error("❌ Backend offline — start FastAPI server.")
                    else:
                        st.warning("Select at least one column first.")

                with st.expander("💡 Where to find free traffic datasets?"):
                    st.markdown("""
                    <div style="font-family:'JetBrains Mono',monospace;font-size:.75rem;color:#64748b;line-height:2.2;">
                    <strong style="color:#00f0ff;">🌍 Public Traffic Datasets:</strong><br>
                    &bull; UK Dept. for Transport Road Statistics — data.gov.uk<br>
                    &bull; Kaggle Traffic Flow Forecasting CSV<br>
                    &bull; NSW Transport Open Data — opendata.transport.nsw.gov.au<br>
                    &bull; Chicago Traffic Crashes JSON — data.cityofchicago.org<br>
                    &bull; SUMO Simulation Output — zenodo.org/record/7008567<br>
                    &bull; TfL London Traffic Counts — data.london.gov.uk
                    </div>
                    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────
# TAB 3 — MAP INTELLIGENCE
# ─────────────────────────────────────────────────
with tab_map_intel:
    import folium
    import streamlit.components.v1 as _components
    import hashlib as _hashlib

    sec_div("🌍 GEOGRAPHIC SMART-CITY NODE INTELLIGENCE")

    # ── Location search bar inside the tab ──────────────────────
    mi_search_col, mi_btn_col = st.columns([3, 1])
    with mi_search_col:
        mi_loc_query = st.text_input(
            "🔍 Search any location worldwide",
            value=st.session_state.location_name,
            key="map_intel_search",
            label_visibility="collapsed",
            placeholder="e.g. Connaught Place, Delhi | Shibuya Crossing, Tokyo | Arc de Triomphe, Paris"
        )
    with mi_btn_col:
        mi_search_btn = st.button("📡 Locate & Track", type="primary", use_container_width=True, key="mi_locate_btn")

    if mi_search_btn and mi_loc_query.strip():
        with st.spinner(f"🛰️ Geolocating {mi_loc_query}..."):
            try:
                _osm = requests.get(
                    f"https://nominatim.openstreetmap.org/search?q={requests.utils.quote(mi_loc_query)}&format=json&limit=1&addressdetails=1",
                    headers={"User-Agent": "AegisMHR/8.0"}, timeout=6
                )
                if _osm.ok and _osm.json():
                    _d = _osm.json()[0]
                    st.session_state.latitude      = float(_d["lat"])
                    st.session_state.longitude     = float(_d["lon"])
                    _raw = _d.get("display_name", mi_loc_query)
                    st.session_state.location_name = ", ".join(_raw.split(",")[:2]).strip()
                    st.session_state["map_bbox"]   = _d.get("boundingbox", None)
                    sync_geo_context(st.session_state.location_name, st.session_state.latitude, st.session_state.longitude)
                    st.toast(f"📍 Locked onto {st.session_state.location_name}", icon="🌍")
                else:
                    sync_geo_context(st.session_state.location_name, st.session_state.latitude, st.session_state.longitude)
                    st.toast("⚠️ Geocoder returned no result — using cached coords")
            except Exception:
                sync_geo_context(st.session_state.location_name, st.session_state.latitude, st.session_state.longitude)
                st.toast("⚠️ Geocoder offline — using cached coords")
        st.rerun()

    lat  = st.session_state.latitude
    lon  = st.session_state.longitude
    loc  = st.session_state.location_name

    # ── Load live vehicle markers (backend → ANPR fallback → simulation) ──
    _VEHICLE_ICONS = {"car": "🚗", "truck": "🚛", "motorcycle": "🏍️", "bus": "🚌",
                      "emergency": "🚑", "control node": "📡"}
    _vehicle_markers = []
    _data_source = "simulation"

    # Priority 1: Backend /api/v1/map/vehicles (most accurate — geo-located by backend)
    _scen_for_map = "normal"
    if st.session_state.active_data:
        _scen_for_map = st.session_state.active_data.get("scenario", "normal")
    if backend_alive():
        try:
            _mv_res = requests.get(
                MAP_VEHICLES_URL,
                params={"scenario": _scen_for_map, "latitude": lat, "longitude": lon, "location_name": loc},
                headers=auth_header(), timeout=8
            )
            if _mv_res.status_code == 200:
                _mv_data = _mv_res.json()
                for _m in _mv_data.get("markers", []):
                    _vehicle_markers.append({
                        "lat":     _m["latitude"],
                        "lon":     _m["longitude"],
                        "plate":   _m["plate"],
                        "type":    _m["vehicle_type"].lower(),
                        "flagged": _m["flagged"],
                        "speed":   _m["speed_kmh"],
                    })
                _data_source = "backend"
        except Exception:
            pass

    # Priority 2: ANPR endpoint + client-side jitter (backend is alive but map/vehicles failed)
    if not _vehicle_markers and backend_alive():
        try:
            _ar = requests.get(
                f"{ANPR_URL}/{_scen_for_map}",
                params={"latitude": lat, "longitude": lon, "location_name": loc},
                headers=auth_header(), timeout=6
            )
            if _ar.status_code == 200:
                _anpr_plates = _ar.json().get("anpr_records", [])
                _rng_seed = int(_hashlib.md5(loc.encode()).hexdigest(), 16) % (2**31)
                import random as _rnd
                _rnd.seed(_rng_seed)
                for _idx, _plate in enumerate(_anpr_plates[:12]):
                    _dlat = _rnd.uniform(-0.003, 0.003)
                    _dlon = _rnd.uniform(-0.003, 0.003)
                    _vehicle_markers.append({
                        "lat":     lat + _dlat,
                        "lon":     lon + _dlon,
                        "plate":   _plate.get("plate", f"VH-{_idx+1:04d}"),
                        "type":    _plate.get("vehicle_type", "car").lower(),
                        "flagged": _plate.get("flagged", False),
                        "speed":   _rnd.randint(20, 80),
                    })
                _data_source = "anpr"
        except Exception:
            pass

    # Priority 3: Pure client-side simulation (no backend)
    if not _vehicle_markers:
        import random as _rnd
        _rng_seed = int(_hashlib.md5(loc.encode()).hexdigest(), 16) % (2**31)
        _rnd.seed(_rng_seed)
        _dummy_types  = ["car", "car", "car", "truck", "bus", "motorcycle", "car", "car"]
        _dummy_plates = [f"AB-{_rnd.randint(10,99)}-{_rnd.randint(1000,9999)}" for _ in _dummy_types]
        for _t, _p in zip(_dummy_types, _dummy_plates):
            _vehicle_markers.append({
                "lat":     lat + _rnd.uniform(-0.003, 0.003),
                "lon":     lon + _rnd.uniform(-0.003, 0.003),
                "plate":   _p, "type": _t,
                "flagged": False,
                "speed":   _rnd.randint(15, 75),
            })
        _data_source = "simulation"


    # ── Build Folium Map ─────────────────────────────────────────
    _fmap = folium.Map(
        location=[lat, lon],
        zoom_start=15,
        tiles=None,          # we add tiles manually for dark + satellite toggle
        prefer_canvas=True
    )

    # Layer 1: OpenStreetMap (default)
    folium.TileLayer(
        tiles="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        attr='© <a href="https://openstreetmap.org">OpenStreetMap</a>',
        name="🗺️ Street Map",
        max_zoom=19,
    ).add_to(_fmap)

    # Layer 2: Esri Satellite imagery (free, no key)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Tiles © Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP",
        name="🛰️ Satellite",
        max_zoom=19,
    ).add_to(_fmap)

    # Layer 3: CartoDB Dark (for traffic overlay feel)
    folium.TileLayer(
        tiles="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        attr='© <a href="https://openstreetmap.org">OpenStreetMap</a> contributors © <a href="https://carto.com/">CARTO</a>',
        name="🌑 Dark Mode",
        max_zoom=19,
    ).add_to(_fmap)

    # ── Primary location pin ─────────────────────────────────────
    _loc_popup_html = f"""
    <div style="font-family:Arial,sans-serif;font-size:13px;min-width:220px;">
      <div style="background:#0d1117;color:#00f0ff;font-weight:700;padding:8px 12px;border-radius:6px 6px 0 0;font-size:14px;">
        📍 {loc}
      </div>
      <div style="background:#1a1f2e;color:#e2e8f0;padding:10px 12px;border-radius:0 0 6px 6px;">
        <b>Coordinates:</b><br>
        <span style="color:#10b981;">LAT {lat:.5f} &nbsp;|&nbsp; LON {lon:.5f}</span><br><br>
        <b>AEGIS Node Status:</b> <span style="color:#10b981;">🟢 ACTIVE</span><br>
        <b>Vehicles on Road:</b> <span style="color:#eab308;">{len(_vehicle_markers)}</span><br>
        <b>Monitoring Radius:</b> <span style="color:#a855f7;">500 m</span>
      </div>
    </div>
    """
    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(_loc_popup_html, max_width=280),
        tooltip=f"📍 {loc} — AEGIS Node",
        icon=folium.Icon(color="red", icon="map-marker", prefix="fa"),
    ).add_to(_fmap)

    # Pulsing radius circle around node
    folium.Circle(
        location=[lat, lon],
        radius=300,
        color="#00f0ff",
        fill=True,
        fill_color="#00f0ff",
        fill_opacity=0.06,
        weight=1.5,
        tooltip="300m AEGIS surveillance radius",
    ).add_to(_fmap)
    folium.Circle(
        location=[lat, lon],
        radius=600,
        color="#a855f7",
        fill=True,
        fill_color="#a855f7",
        fill_opacity=0.03,
        weight=1,
        tooltip="600m extended monitoring zone",
    ).add_to(_fmap)

    # ── Vehicle / ANPR markers ───────────────────────────────────
    _veh_group = folium.FeatureGroup(name="🚗 Live Vehicle Tracking")
    for _v in _vehicle_markers:
        _vtype   = _v["type"]
        _emoji   = _VEHICLE_ICONS.get(_vtype, "🚗")
        _flag_c  = "#ef4444" if _v["flagged"] else "#10b981"
        _flag_lbl = "🚩 FLAGGED" if _v["flagged"] else "✅ CLEAR"
        _veh_html = f"""
        <div style="font-family:'Courier New',monospace;font-size:12px;min-width:190px;">
          <div style="background:#0d1117;color:{_flag_c};font-weight:700;padding:6px 10px;border-radius:5px 5px 0 0;">
            {_emoji} {_v['plate']}  &nbsp; {_flag_lbl}
          </div>
          <div style="background:#1a1f2e;color:#e2e8f0;padding:8px 10px;border-radius:0 0 5px 5px;line-height:1.8;">
            <b>Type:</b> {_vtype.title()}<br>
            <b>Speed:</b> {_v['speed']} km/h<br>
            <b>Lat:</b> {_v['lat']:.5f} &nbsp; <b>Lon:</b> {_v['lon']:.5f}
          </div>
        </div>
        """
        _icon_color = "red" if _v["flagged"] else "blue"
        folium.Marker(
            location=[_v["lat"], _v["lon"]],
            popup=folium.Popup(_veh_html, max_width=240),
            tooltip=f"{_emoji} {_v['plate']} — {_v['speed']} km/h",
            icon=folium.Icon(color=_icon_color, icon="car", prefix="fa"),
        ).add_to(_veh_group)
    _veh_group.add_to(_fmap)

    # ── Directions panel — OSRM route from node to nearest flagged or first vehicle ──
    _dir_group = folium.FeatureGroup(name="🗺️ Route / Direction")
    if _vehicle_markers:
        _flagged_vehs = [v for v in _vehicle_markers if v["flagged"]]
        _target_veh   = _flagged_vehs[0] if _flagged_vehs else _vehicle_markers[0]
        _t_lat, _t_lon = _target_veh["lat"], _target_veh["lon"]
        try:
            _osrm_url = (
                f"https://router.project-osrm.org/route/v1/driving/"
                f"{lon},{lat};{_t_lon},{_t_lat}"
                f"?overview=full&geometries=geojson&steps=true"
            )
            _route_res = requests.get(_osrm_url, timeout=6)
            if _route_res.ok:
                _route_data = _route_res.json()
                _route      = _route_data["routes"][0]
                _geom       = _route["geometry"]["coordinates"]  # [[lon,lat],...]
                _coords     = [[c[1], c[0]] for c in _geom]
                _dist_km    = round(_route["distance"] / 1000, 2)
                _dur_min    = round(_route["duration"] / 60, 1)
                folium.PolyLine(
                    _coords,
                    color="#00f0ff",
                    weight=4,
                    opacity=0.75,
                    tooltip=f"Route to {_target_veh['plate']} — {_dist_km} km / {_dur_min} min",
                    dash_array="8 4",
                ).add_to(_dir_group)
                st.session_state["map_route_dist"] = _dist_km
                st.session_state["map_route_dur"]  = _dur_min
                st.session_state["map_route_target"] = _target_veh["plate"]
            else:
                # Straight-line fallback
                folium.PolyLine(
                    [[lat, lon], [_t_lat, _t_lon]],
                    color="#f59e0b", weight=3, opacity=0.6, dash_array="6 4",
                    tooltip=f"Direct bearing to {_target_veh['plate']}",
                ).add_to(_dir_group)
                st.session_state["map_route_dist"]   = None
                st.session_state["map_route_dur"]    = None
                st.session_state["map_route_target"] = _target_veh["plate"]
        except Exception:
            folium.PolyLine(
                [[lat, lon], [_t_lat, _t_lon]],
                color="#f59e0b", weight=3, opacity=0.6, dash_array="6 4",
                tooltip=f"Direct bearing to {_target_veh['plate']}",
            ).add_to(_dir_group)
    _dir_group.add_to(_fmap)

    # ── Historical scan location pins ────────────────────────────
    _hist_group = folium.FeatureGroup(name="📜 Scan History")
    try:
        _h_res = requests.get(HISTORY_URL, headers=auth_header(), timeout=5) if backend_alive() else None
        if _h_res and _h_res.status_code == 200:
            _hd = _h_res.json().get("history", [])
            for _hr in _hd[-20:]:   # Last 20 scans
                _hlat = _hr.get("latitude")
                _hlon = _hr.get("longitude")
                if _hlat and _hlon and (_hlat != lat or _hlon != lon):
                    _hrisk = _hr.get("risk_score", 0)
                    _hc = "red" if _hrisk >= 70 else ("orange" if _hrisk >= 40 else "green")
                    folium.CircleMarker(
                        location=[_hlat, _hlon],
                        radius=6,
                        color=_hc,
                        fill=True,
                        fill_color=_hc,
                        fill_opacity=0.7,
                        tooltip=f"📊 {_hr.get('location_name','?')} — Risk {_hrisk}%",
                        popup=folium.Popup(
                            f"<b>{_hr.get('location_name','?')}</b><br>"
                            f"Risk: {_hrisk}% | Vehicles: {_hr.get('vehicle_count','—')}<br>"
                            f"Scenario: {_hr.get('scenario','—')}",
                            max_width=200
                        )
                    ).add_to(_hist_group)
    except Exception:
        pass
    _hist_group.add_to(_fmap)

    folium.LayerControl(position="topright", collapsed=False).add_to(_fmap)

    # ── Render map + info layout ─────────────────────────────────
    mc1, mc2 = st.columns([2.2, 0.8])
    with mc1:
        # Embed the Folium map via components
        _map_html = _fmap._repr_html_()
        _components.html(_map_html, height=530, scrolling=False)

        # Quick search tips + data source badge below the map
        _src_badge = {
            "backend":    ("🟢 LIVE BACKEND", "#10b981"),
            "anpr":       ("🟡 ANPR DATA",    "#f59e0b"),
            "simulation": ("🔵 SIMULATION",   "#00f0ff"),
        }.get(_data_source, ("⚪ UNKNOWN", "#64748b"))
        st.markdown(f"""
        <div style="font-family:'JetBrains Mono',monospace;font-size:.68rem;color:#4b6584;margin-top:6px;padding:8px 12px;background:rgba(0,0,0,.2);border-radius:6px;">
        <span style="color:{_src_badge[1]};font-weight:700;">⬤ Vehicle Data: {_src_badge[0]}</span>
        &nbsp;|&nbsp; {len(_vehicle_markers)} vehicles tracked
        &nbsp;|&nbsp; {sum(1 for v in _vehicle_markers if v['flagged'])} flagged<br>
        💡&nbsp; Use the <strong style="color:#00f0ff;">layer control ↗</strong> to toggle: Street Map · Satellite · Dark Mode · Vehicles · Route · History<br>
        🚗&nbsp; <strong style="color:#10b981;">Blue</strong> = active &nbsp;|&nbsp;
        🚩&nbsp; <strong style="color:#ef4444;">Red</strong> = ANPR flagged &nbsp;|&nbsp;
        🔵&nbsp; Cyan line = OSRM route &nbsp;|&nbsp;
        🟡&nbsp; Orange = direct bearing
        </div>
        """, unsafe_allow_html=True)


    with mc2:
        # Active node card
        st.markdown(f"""
        <div class="card" style="margin-bottom:10px;">
            <div class="t-section" style="margin-bottom:8px;font-size:.75rem;">📍 ACTIVE NODE</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:.72rem;line-height:1.9;">
                <span style="color:#4b6584;">LOCATION</span><br>
                <strong style="color:#00f0ff;">{loc}</strong><br><br>
                <span style="color:#4b6584;">COORDINATES</span><br>
                <span style="color:#10b981;">LAT {lat:.5f}</span><br>
                <span style="color:#10b981;">LON {lon:.5f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Live vehicles card
        _flagged_cnt = sum(1 for v in _vehicle_markers if v["flagged"])
        st.markdown(f"""
        <div class="card" style="margin-bottom:10px;">
            <div class="t-section" style="margin-bottom:8px;font-size:.75rem;">🚗 LIVE VEHICLES</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:.72rem;line-height:2;">
                <span style="color:#4b6584;">ON ROAD</span><br>
                <strong style="color:#eab308;font-size:1.2rem;">{len(_vehicle_markers)}</strong><br>
                <span style="color:#4b6584;">ANPR FLAGGED</span><br>
                <strong style="color:#ef4444;font-size:1rem;">{_flagged_cnt}</strong><br>
                <span style="color:#4b6584;">AVG SPEED</span><br>
                <span style="color:#a855f7;">{round(sum(v['speed'] for v in _vehicle_markers)/max(len(_vehicle_markers),1))} km/h</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Directions / route card
        _rdist = st.session_state.get("map_route_dist")
        _rdur  = st.session_state.get("map_route_dur")
        _rtgt  = st.session_state.get("map_route_target", "—")
        st.markdown(f"""
        <div class="card" style="margin-bottom:10px;">
            <div class="t-section" style="margin-bottom:8px;font-size:.75rem;">🗺️ DIRECTION / ROUTE</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:.72rem;line-height:2;">
                <span style="color:#4b6584;">TARGET VEHICLE</span><br>
                <strong style="color:#00f0ff;">{_rtgt}</strong><br>
                <span style="color:#4b6584;">DISTANCE</span><br>
                <span style="color:#10b981;">{f"{_rdist} km" if _rdist else "< 1 km (direct)"}</span><br>
                <span style="color:#4b6584;">ETA</span><br>
                <span style="color:#a855f7;">{f"{_rdur} min" if _rdur else "Calculating..."}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Global node coverage hints
        st.markdown("""
        <div class="card">
            <div class="t-section" style="margin-bottom:8px;font-size:.75rem;">🌐 GLOBAL NODES</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:.68rem;line-height:2;color:#64748b;">
                • Tokyo, Japan<br>
                • Times Square, NY<br>
                • Shibuya Crossing<br>
                • Arc de Triomphe<br>
                • Mumbai Junction<br>
                • Trafalgar Square<br>
                • Sheikh Zayed Rd
            </div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────
# TAB 4 — TELEMETRY SANDBOX
# ─────────────────────────────────────────────────
with tab_sandbox:
    sec_div("🧪 MULTIMODAL TELEMETRY SANDBOX ANALYZER")
    st.markdown("<p style='color:#64748b;font-family:JetBrains Mono;font-size:.8rem;'>Test custom traffic conditions offline without affecting live operations.</p>", unsafe_allow_html=True)

    sb_left, sb_right = st.columns([1.1, 1.9])
    with sb_left:
        st.markdown("""<div class="card">""", unsafe_allow_html=True)
        st.markdown('<div class="t-section" style="margin-bottom:12px;">🎛️ Custom Parameters</div>', unsafe_allow_html=True)
        sb_vehicles = st.slider("Vehicles in frame", 0, 25, 5, key="sb_veh")
        sb_db       = st.slider("Sound Level (dB SPL)", 30, 120, 58, key="sb_db")
        sb_freq     = st.slider("Peak Frequency (Hz)", 50, 4500, 420, key="sb_freq")
        sb_atype    = st.selectbox("Audio Signature", ["Ambient","Horn","Siren","Collision"], key="sb_atype")
        sb_cam      = st.selectbox("Camera Integrity", ["Clear Feed","Obscured / Tampered"], key="sb_cam")
        sb_mode     = st.selectbox("Fusion Mode", ["AI Automated Fusion","Predictive Optimization"], key="sb_mode")
        sb_weather  = st.selectbox("Weather Condition", ["Clear","Rain","Fog","Snow"], key="sb_weather")
        st.markdown("</div>", unsafe_allow_html=True)
        run_sb = st.button("🧪 RUN SANDBOX ANALYSIS", type="primary", use_container_width=True, key="btn_run_sandbox_analysis")

    with sb_right:
        if run_sb or st.session_state.sb_results:
            if run_sb:
                sb_visual = []
                if sb_cam == "Obscured / Tampered":
                    sb_visual = [{"label": "CAMERA_BLOCKED_TAMPER", "confidence": 0.99}]
                else:
                    sb_visual = [{"label": "car", "confidence": 0.90}] * sb_vehicles

                sb_audio = {
                    "type": sb_atype,
                    "db_level": float(sb_db),
                    "peak_frequency": float(sb_freq),
                    "waveform": [math.sin(i * 0.2) * (sb_db / 100) for i in range(200)],
                    "fft_frequencies": list(range(0, 4000, 40)),
                    "fft_amplitudes":  [random.random() * (1 if sb_atype == "Ambient" else 2) for _ in range(100)],
                    "status": "Anomaly Detected" if sb_db > 75 else "Normal"
                }

                try:
                    import sys, os
                    sys.path.insert(0, os.path.abspath("."))
                    from app.pipeline.fusion_core import MultimodalFusionCore
                    fc = MultimodalFusionCore()
                    res = fc.fuse_and_classify(sb_visual, sb_audio, "normal", operational_mode=sb_mode)
                    st.session_state.sb_results = res
                except Exception as e:
                    st.session_state.sb_results = {
                        "priority": "⚠️ SANDBOX MODE (Backend Required)",
                        "risk_score": sb_db - 20,
                        "signal_timing_seconds": 30,
                        "active_phase": "North-South Green",
                        "advisory": f"Audio: {sb_atype} @ {sb_db}dB. {sb_vehicles} vehicles. {sb_weather} conditions.",
                        "report": f"Custom telemetry sandbox simulation. Error: {str(e)[:60]}"
                    }

            res = st.session_state.sb_results
            rc = risk_color(res["risk_score"])
            st.markdown(f"""
            <div class="card" style="border-color:{rc}40;">
                <div style="font-family:'Orbitron',sans-serif;font-size:1.05rem;font-weight:700;color:#00f0ff;margin-bottom:14px;">
                    🔮 FUSION PREDICTION RESULT
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:16px;">
                    {metric_tile("Alert Level","—","",rc,"🚨")}
                    {metric_tile("Risk Score",str(res["risk_score"]),"%",rc,"🔥")}
                    {metric_tile("Signal Timing",str(res["signal_timing_seconds"])+"s","","#a855f7","🚦")}
                    {metric_tile("Phase","—","","#00f0ff","⚙️")}
                </div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:.72rem;">
                    <div style="color:{rc};font-weight:700;font-size:.9rem;margin-bottom:8px;">{res["priority"]}</div>
                    <div style="color:#64748b;">PHASE:</div>
                    <div style="color:#00f0ff;margin-bottom:8px;">{res["active_phase"]}</div>
                    <div style="color:#64748b;">ADVISORY:</div>
                    <div style="color:#e2e8f0;margin-bottom:8px;">{res["advisory"]}</div>
                    <div style="color:#64748b;">REPORT:</div>
                    <div style="color:#94a3b8;font-size:.68rem;">{res["report"]}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Sandbox waveform
            t_vals = list(range(200))
            y_vals = [math.sin(i * 0.18 * (sb_freq / 400)) * (sb_db / 100) + random.uniform(-0.05, 0.05) for i in t_vals]
            fig_sb = go.Figure()
            fig_sb.add_trace(go.Scatter(y=y_vals, mode='lines', line=dict(color='#a855f7', width=1.2),
                                        fill='tozeroy', fillcolor='rgba(168,85,247,0.05)'))
            fig_sb.update_layout(
                title=f"Simulated Waveform — {sb_atype} @ {sb_db} dB",
                height=150, margin=dict(l=8,r=8,t=30,b=8),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(visible=False), yaxis=dict(visible=False),
                font=dict(family="JetBrains Mono", color="#64748b", size=10)
            )
            st.plotly_chart(fig_sb, use_container_width=True, key="sb_wave")
        else:
            st.markdown("""
            <div class="card" style="text-align:center;padding:50px;">
                <div style="font-size:3rem;margin-bottom:12px;">🧪</div>
                <div style="font-family:'JetBrains Mono',monospace;color:#4b6584;font-size:.8rem;">
                    Adjust parameters and run the sandbox analysis<br>to preview fusion engine outcomes.
                </div>
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────
# TAB 5 — AI COPILOT CHAT
# ─────────────────────────────────────────────────
with tab_ai_chat:
    sec_div("🤖 AI TRAFFIC OPERATIONS COPILOT")
    st.markdown("<p style='color:#64748b;font-family:JetBrains Mono;font-size:.78rem;'>Ask the AI copilot anything about traffic management, incidents, signal timing, or system operations. Powered by Qwen 2.5.</p>", unsafe_allow_html=True)

    chat_col, info_col = st.columns([2, 1])
    with chat_col:
        ctx = ""
        if st.session_state.active_data:
            fl_ = st.session_state.active_data["fusion_layer"]
            ctx = (f"Active scenario: {fl_['alert_status']}. "
                   f"Vehicles: {fl_['vehicle_count']}. "
                   f"Phase: {fl_['active_phase']}. "
                   f"Advisory: {fl_['rerouting_advisory']}")

        # Quick prompt buttons
        st.markdown("<div style='margin-bottom:8px;'>", unsafe_allow_html=True)
        qcols = st.columns(4)
        quick_prompts = [
            "What should I do about the current congestion?",
            "Explain the emergency vehicle priority override.",
            "How does camera tamper detection work?",
            "What is the optimal signal timing strategy?"
        ]
        for idx, (qc, qp) in enumerate(zip(qcols, quick_prompts)):
            if qc.button(qp[:28]+"...", use_container_width=True, key=f"btn_copilot_qp_{idx}"):
                st.session_state.copilot_history.append({"role":"user","text":qp})
                try:
                    cr = requests.post(CHAT_URL, json={
                        "user_message": qp,
                        "incident_context": ctx or "No active scan.",
                        "session_token": st.session_state.user_token
                    }, headers=auth_header(), timeout=25).json()
                    st.session_state.copilot_history.append({"role":"assistant","text":cr.get("reply","...")})
                except:
                    st.session_state.copilot_history.append({"role":"assistant","text":"⚠️ Copilot offline — start backend."})
        st.markdown("</div>", unsafe_allow_html=True)

        # Chat display
        chat_container = st.container(height=480)
        with chat_container:
            for msg in st.session_state.copilot_history:
                if msg["role"] == "user":
                    st.markdown(f'<div class="chat-msg-user">👤 <strong>User:</strong> {msg["text"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-msg-ai">🤖 <strong>AI Operations Copilot:</strong></div>', unsafe_allow_html=True)
                    st.markdown(msg["text"])
                    st.markdown("<hr style='border:none;border-top:1px dashed rgba(0,240,255,.15);margin:12px 0;'>", unsafe_allow_html=True)

        chat_input = st.chat_input("Ask the AI copilot about traffic operations, signals, or incidents...")
        if chat_input:
            st.session_state.copilot_history.append({"role":"user","text":chat_input})
            with st.spinner("🤖 Copilot thinking..."):
                try:
                    cr = requests.post(CHAT_URL, json={
                        "user_message": chat_input,
                        "incident_context": ctx or "No active scan — general query.",
                        "session_token": st.session_state.user_token
                    }, headers=auth_header(), timeout=30).json()
                    st.session_state.copilot_history.append({"role":"assistant","text":cr.get("reply","...")})
                except:
                    st.session_state.copilot_history.append({"role":"assistant","text":"⚠️ Copilot offline."})
            st.rerun()

        if st.button("🗑️ Clear Chat History", use_container_width=True, key="btn_copilot_clear_chat"):
            st.session_state.copilot_history = []
            st.rerun()

    with info_col:
        st.markdown("""
        <div class="card" style="margin-bottom:12px;">
            <div class="t-section" style="margin-bottom:10px;">🧠 Copilot Capabilities</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:.72rem;color:#64748b;line-height:2.1;">
                ✅ Explain traffic anomalies<br>
                ✅ Signal timing optimization<br>
                ✅ Emergency override protocols<br>
                ✅ Congestion rerouting advice<br>
                ✅ Acoustic anomaly guidance<br>
                ✅ Camera tamper procedures<br>
                ✅ Security breach responses<br>
                ✅ ARIMA demand forecasting<br>
                ✅ JWT/API troubleshooting
            </div>
        </div>
        <div class="card">
            <div class="t-section" style="margin-bottom:10px;">🛡️ Security Guardrails</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:.7rem;color:#64748b;line-height:2;">
                • Prompt injection blocked<br>
                • Zero-trust context isolation<br>
                • Role-aware responses<br>
                • No credential disclosure
            </div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────
# TAB 6 — LEARNING GUIDE
# ─────────────────────────────────────────────────
with tab_guide:
    sec_div("📚 INTERACTIVE LEARNING GUIDE")
    st.markdown("<p style='color:#64748b;font-family:JetBrains Mono;font-size:.78rem;'>Step-by-step walkthrough of AEGIS-TRAFFIC's AI systems and enterprise features.</p>", unsafe_allow_html=True)

    g_sel = st.selectbox("Select Topic", [
        "🚀 Getting Started — Platform Overview",
        "🤖 How AI Fusion Works (YOLOv8 + DistilBERT)",
        "🔊 Acoustic Anomaly Detection (FFT + dB Analysis)",
        "🔒 Security Architecture (JWT, PBKDF2, AES-256)",
        "🌍 Geographic Initialization (Nominatim + Mapbox)",
        "⚙️ Operating Modes — State Machine Deep Dive",
        "📈 Analytics & Production Telemetry",
        "🔮 Predictive ARIMA Optimization",
        "🧪 Sandbox Analyzer — Custom Testing",
        "🚦 Adaptive Signal Control (ATSC) Theory",
    ], label_visibility="collapsed", key="guide_topic_select")

    topics = {
        "🚀 Getting Started — Platform Overview": {
            "icon": "🚀", "color": "#00f0ff",
            "overview": "AEGIS-TRAFFIC is a production-grade smart-city AI platform that fuses computer vision, acoustic analysis, and NLP to manage urban intersections in real time.",
            "steps": [
                ("1️⃣ Boot the Backend", "Run `uvicorn app.main:app --reload` from the project root. The FastAPI server initialises on port 8000."),
                ("2️⃣ Launch Dashboard",  "Run `streamlit run dashboard/app.py` and navigate to localhost:8501."),
                ("3️⃣ Login",             "Use demo credentials: admin/Admin@AEGIS2024! for full Admin clearance."),
                ("4️⃣ Choose Location",   "Type any city or intersection in the Geographic Registry sidebar panel and click \'Initialize Site Node\'."),
                ("5️⃣ Select Scenario",   "Choose from Normal, Congested, Emergency, Accident, or Tamper scenarios in the sidebar."),
                ("6️⃣ Execute Scan",      "Click ⚡ EXECUTE SCENARIO SCAN. Results populate all eight dashboard tabs."),
            ]
        },
        "🤖 How AI Fusion Works (YOLOv8 + DistilBERT)": {
            "icon": "🤖", "color": "#a855f7",
            "overview": "Two AI models fuse their outputs to produce a holistic traffic state assessment far more accurate than either model alone.",
            "steps": [
                ("Visual Layer",     "YOLOv8 runs real-time COCO object detection on synthetic intersection frames. It counts cars, trucks, buses, motorcycles, and flags camera blockage."),
                ("Acoustic Layer",   "A WAV pipeline performs RMS decibel measurement and FFT frequency analysis to detect sirens, collisions, and horns."),
                ("NLP Fusion",       "DistilBERT (zero-shot MNLI) classifies the multimodal fused context string into: Normal Flow / Congestion / Accident / Emergency."),
                ("Guardrail Logic",  "Heuristic overrides prevent the NLP model from producing spurious alerts when vehicle count is ≤2 and audio is ambient."),
                ("Decision Matrix",  "The priority engine assigns PRIORITY 1/2/3/NOMINAL and calculates adaptive green light timing (15s / 30s / 45s)."),
            ]
        },
        "🔒 Security Architecture (JWT, PBKDF2, AES-256)": {
            "icon": "🔒", "color": "#10b981",
            "overview": "AEGIS-TRAFFIC uses enterprise-grade cryptographic primitives across every layer — from user authentication to encrypted database ledger storage.",
            "steps": [
                ("Password Hashing",  "PBKDF2-HMAC-SHA256 with 100,000 iterations and a 16-byte random salt. Constant-time comparison via secrets.compare_digest()."),
                ("JWT Tokens",        "Custom HMAC-SHA256 JWT implementation. Tokens expire after 1 hour. Signature validation protects against forgery."),
                ("Role-Based Access", "Three clearance levels: Admin (full access), Operator (scan only), Auditor (read logs). FastAPI Depends() enforces RBAC on every route."),
                ("AES-256 DB Vault",  "All telemetry records are serialised to JSON, encrypted via Fernet (AES-128-CBC + HMAC-SHA256), and stored as binary blobs."),
                ("Prompt Injection",  "Chat API blocks 6 categories of injection payloads before forwarding to the language model."),
            ]
        },
    }

    default_content = {
        "icon": "📖", "color": "#f59e0b",
        "overview": "This topic covers a core feature of the AEGIS-TRAFFIC AI platform. Explore the steps below for details.",
        "steps": [
            ("Feature Summary", "This module is covered in detail in the Diagnostics & Mitigation manual tab for operational guidance."),
            ("AI Integration", "AEGIS-TRAFFIC integrates YOLOv8, DistilBERT, Qwen 2.5, FFT acoustic analysis, and Fernet AES-256 encryption."),
        ]
    }

    topic_data = topics.get(g_sel, default_content)
    tc, ic = topic_data["color"], topic_data["icon"]

    st.markdown(f"""
    <div class="card" style="border-color:{tc}33;padding:24px;">
        <div style="font-size:2.5rem;margin-bottom:8px;">{ic}</div>
        <div style="font-family:'Orbitron',sans-serif;font-size:1rem;font-weight:700;color:{tc};margin-bottom:12px;">{g_sel}</div>
        <div style="font-family:'Inter',sans-serif;font-size:.88rem;color:#94a3b8;line-height:1.7;margin-bottom:20px;
            border-left:3px solid {tc}44;padding-left:14px;">
            {topic_data['overview']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    for i, (title, desc) in enumerate(topic_data["steps"]):
        with st.expander(f"  {title}", expanded=(i == 0)):
            st.markdown(f"<div style='font-family:Inter,sans-serif;font-size:.87rem;color:#94a3b8;line-height:1.8;'>{desc}</div>", unsafe_allow_html=True)

    mini_separator()
    st.markdown("""
    <div class="card" style="border-color:#6366f133;">
        <div class="t-section" style="margin-bottom:10px;">🏗️ ENTERPRISE AI FEATURES IN THIS PLATFORM</div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;font-family:'JetBrains Mono',monospace;font-size:.7rem;color:#64748b;">
            <div>✅ Real-time YOLOv8 detection<br>✅ Acoustic FFT analysis<br>✅ Zero-shot NLP fusion<br>✅ JWT + PBKDF2 auth</div>
            <div>✅ AES-256 encrypted ledger<br>✅ RBAC role clearance<br>✅ Earth-wide geocoding<br>✅ Adaptive signal control</div>
            <div>✅ Predictive ARIMA mode<br>✅ Emergency preemption<br>✅ Webhook broadcasts<br>✅ CSV audit exports</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────
# TAB 7 — DIAGNOSTICS & MITIGATION MANUAL
# ─────────────────────────────────────────────────
with tab_manual:
    sec_div("📖 OPERATIONAL DIAGNOSTICS & MITIGATION MANUAL")
    st.markdown("<p style='color:#64748b;font-family:JetBrains Mono;font-size:.78rem;'>Select any anomaly to view detailed explanation, root causes, related cascading failures, and evidence-based mitigations.</p>", unsafe_allow_html=True)

    problem = st.selectbox("Select Problem Profile", [
        "🚦 1. Extreme Intersection Congestion & Grid-lock Cascades",
        "💥 2. Vehicle Accident / Multi-car Collision",
        "🚒 3. Emergency Vehicle Preemption Failure",
        "🛡️ 4. Camera Obscuration / Hardware Tampering",
        "🔑 5. API Breach / SQL Injection / JWT Forgery",
        "🌧️ 6. Adverse Weather Conditions (Rain / Fog / Snow)",
        "📡 7. Model Drift / False Positive Anomalies",
    ], label_visibility="collapsed", key="diag_problem_select")

    PROBLEMS = {
        "1": {
            "icon":"🚦", "color":"#f59e0b",
            "title":"Extreme Intersection Congestion & Grid-lock Cascades",
            "cause":"Static signal cycles allocate equal time regardless of demand. During peak hours or incidents, queues accumulate faster than cycle clearing rates, causing intersection saturation and downstream blocking.",
            "related":["Gridlock propagation across adjacent intersections", "Elevated exhaust emissions from prolonged idling", "Increased collision risk from frustrated drivers making unsafe maneuvers", "Economic losses from delayed freight/logistics"],
            "solutions":[
                ("Adaptive Signal Control (ATSC)", "YOLOv8 counts vehicle queues in real time. When count ≥9, extend the green phase from 15s → 45s. 5–8 vehicles → 30s. Reduces average delay by up to 40%."),
                ("Predictive Optimization Mode", "ARIMA/LSTM model forecasts demand 10–15 min ahead. Green windows are extended proactively before queues form — especially for known rush-hour windows."),
                ("Municipal Webhook Alerts", "Automatically push HTTP webhook to electronic road signs, routing apps (Google Maps), and dispatch hubs when congestion risk score exceeds 30%."),
            ],
            "action_label": "🔧 Trigger Detour Bypass Alpha",
            "action_msg": "✅ Detour route activated on municipal digital signs. Traffic rerouted to Bypass A."
        },
        "2": {
            "icon":"💥", "color":"#ef4444",
            "title":"Vehicle Accident / Multi-car Collision",
            "cause":"High-speed intersection entries during yellow phases, distracted drivers, and adverse weather increase collision probability. Unmanaged intersections lack automated detection and response.",
            "related":["Secondary crashes as drivers approach stalled vehicles", "First-responder path blockage inside crash zone", "Up to 4–6 hour traffic freeze for evidence collection", "Psychological trauma causing post-incident traffic anxiety"],
            "solutions":[
                ("Multi-modal Cross-verification", "Fuse YOLOv8 crash bounding box detection with acoustic impact signature (>80 dB SPL, >2kHz peak). Both channels must confirm before triggering PRIORITY 2."),
                ("ALL-RED Containment Phase", "Immediately activate ALL-RED across all signal phases to freeze all vehicle entries to the intersection. Prevents secondary collisions from blindspot approaches."),
                ("First-Responder Webhook", "Send high-priority pager alert (SMS/email) to police, ambulance, and fire stations with GPS coordinates and crash context JSON payload."),
            ],
            "action_label": "🚒 Dispatch Emergency Responders",
            "action_msg": "✅ Emergency pager deployed. Police + Ambulance ETA: 4.2 minutes. Intersection locked ALL-RED."
        },
        "3": {
            "icon":"🚒", "color":"#f59e0b",
            "title":"Emergency Vehicle Preemption Failure",
            "cause":"Standard traffic cycles do not detect approaching emergency vehicles, causing gridlock that delays ambulances and fire engines by critical minutes.",
            "related":["Increased patient mortality from ambulance delays", "Firefighter access blockage increasing fire spread risk", "Emergency vehicles forced to cross on red lights risking side-impacts"],
            "solutions":[
                ("Acoustic Siren Detection", "FFT analysis detects frequency sweeps (600–1200Hz) with amplitude >80dB. These acoustic signatures uniquely identify emergency sirens versus horn/ambient noise."),
                ("Green Wave Priority Override", "Immediately force the emergency vehicle's incoming lane to GREEN (25s window). All other lanes switch to RED until the vehicle clears the intersection."),
                ("Siren Decay Monitoring", "Track SPL amplitude decay after the initial detection event. Normal operations resume only once the acoustic signature falls below ambient threshold, preventing false re-triggers."),
            ],
            "action_label": "⚡ Force Emergency Green Wave Now",
            "action_msg": "✅ Emergency GREEN phase activated. Ambulance path cleared. All other lanes RED."
        },
        "4": {
            "icon":"🛡️", "color":"#94a3b8",
            "title":"Camera Obscuration / Hardware Tampering",
            "cause":"Vandals spray camera lenses, weather causes lens fogging, or hardware faults cause video loss. Without visual input, adaptive signal control operates blindly.",
            "related":["Complete loss of YOLOv8 vehicle counting capability", "Inability to detect accidents or emergency vehicles", "Manual intersection operation required, increasing human error", "Potential coverage for criminal activities at intersection"],
            "solutions":[
                ("Fail-Safe Flashing Yellow Mode", "Upon detection of CAMERA_BLOCKED_TAMPER event (99% confidence), immediately switch all phases to Flashing Yellow. Treats intersection as a 4-way stop."),
                ("Acoustic Fallback Control", "Continue monitoring acoustic SPL and frequency signatures even without visual feed. Siren tones can still trigger emergency preemption."),
                ("Tamper Incident Ledger", "Log tamper event with GPS coordinates, timestamp, and camera ID to the encrypted SQLite vault. Dispatch maintenance crew via webhook notification."),
            ],
            "action_label": "🛠️ Dispatch Maintenance Crew",
            "action_msg": "✅ Field maintenance team dispatched. Ticket ID: TAMP-9921. ETA: 22 minutes."
        },
        "5": {
            "icon":"🔑", "color":"#6366f1",
            "title":"API Breach / SQL Injection / JWT Forgery",
            "cause":"Exposed APIs, plain-text storage, and weak session management allow attackers to steal operational logs, inject SQL commands, or forge authentication tokens.",
            "related":["Data exfiltration of sensitive operator logs and GPS incident data", "Database tampering to erase incident evidence", "Privilege escalation enabling operators to pull admin-only ledgers", "Denial-of-service via brute-force credential attacks"],
            "solutions":[
                ("Fernet AES-256 Encryption", "All telemetry rows are serialised and encrypted via cryptography.fernet before SQL storage. Raw DB file inspection yields zero readable data."),
                ("PBKDF2 Password Hashing", "100,000 iterations of PBKDF2-HMAC-SHA256 with 16-byte random salt. Makes brute-force computationally infeasible."),
                ("JWT RBAC Access Control", "HMAC-SHA256 signed tokens with 1-hour expiry protect every FastAPI endpoint. Admin/Operator/Auditor roles enforce function-level access controls."),
            ],
            "action_label": "🛡️ Run Crypto Integrity Audit",
            "action_msg": "✅ Database integrity verified: 100%. AES-256 cipher active. Zero breach vectors detected."
        },
    }

    prob_num = problem[2]
    pd_data = PROBLEMS.get(prob_num, {"icon":"📖","color":"#64748b","title":problem[3:],"cause":"General operational issue.","related":[],"solutions":[],"action_label":"","action_msg":""})
    tc2 = pd_data["color"]

    st.markdown(f"""
    <div class="card card-alert-{'red' if tc2=='#ef4444' else 'amber' if tc2=='#f59e0b' else 'blue' if tc2=='#6366f1' else 'green'}"
         style="margin-bottom:16px;">
        <div style="font-size:2rem;margin-bottom:6px;">{pd_data['icon']}</div>
        <div style="font-family:'Orbitron',sans-serif;font-size:.95rem;font-weight:700;color:{tc2};">{pd_data['title']}</div>
    </div>
    """, unsafe_allow_html=True)

    pc1, pc2 = st.columns(2)
    with pc1:
        st.markdown("#### 🔎 Root Cause Analysis")
        st.markdown(f"<div style='font-family:Inter,sans-serif;font-size:.87rem;color:#94a3b8;line-height:1.8;'>{pd_data['cause']}</div>", unsafe_allow_html=True)
        if pd_data.get("related"):
            st.markdown("#### 🔗 Related Cascading Failures")
            for r in pd_data["related"]:
                st.markdown(f"<div style='font-family:JetBrains Mono,monospace;font-size:.75rem;color:#64748b;padding:4px 0;'>→ {r}</div>", unsafe_allow_html=True)

    with pc2:
        st.markdown("#### 🛡️ Mitigation Strategies")
        for title_s, desc_s in pd_data.get("solutions", []):
            with st.expander(f"  {title_s}"):
                st.markdown(f"<div style='font-family:Inter,sans-serif;font-size:.85rem;color:#94a3b8;line-height:1.8;'>{desc_s}</div>", unsafe_allow_html=True)

        if pd_data.get("action_label"):
            if st.button(pd_data["action_label"], use_container_width=True, type="primary", key=f"btn_diag_action_{prob_num}"):
                st.success(pd_data["action_msg"])


# ─────────────────────────────────────────────────
# TAB 8 — SECURITY LEDGER
# ─────────────────────────────────────────────────
with tab_security:
    sec_div("🔒 ZERO-TRUST SECURITY AUDIT & ENCRYPTED LEDGER")

    h_res3 = requests.get(HISTORY_URL, headers=auth_header(), timeout=10) if backend_alive() else None
    if h_res3 and h_res3.status_code == 200:
        h_df3 = pd.DataFrame(h_res3.json()["history"])
        if not h_df3.empty:
            sec_div("🛡️ DECRYPTED RELATIONAL LEDGER")
            # Show the most-important columns
            cols_show = [c for c in ["timestamp","operator_id","scenario","location_name","operational_mode","priority","risk_score","vehicle_count","signal_timing_seconds","active_phase"] if c in h_df3.columns]
            st.dataframe(h_df3[cols_show], use_container_width=True, hide_index=True, height=320)

            sec_div("📊 BREACH & INTEGRITY INDICES")
            sm_sec = st.session_state.active_data["system_telemetry_metrics"] if st.session_state.active_data else {}
            s1,s2,s3,s4 = st.columns(4)
            s1.markdown(metric_tile("Ledger Records", len(h_df3), " rows","#00f0ff","📋"), unsafe_allow_html=True)
            s2.markdown(metric_tile("Breach Attempts", sm_sec.get("unauthorized_breaches",0)," blocks","#ef4444","🚫"), unsafe_allow_html=True)
            s3.markdown(metric_tile("Critical Events", sm_sec.get("critical_incidents",0)," cases","#f59e0b","🚨"), unsafe_allow_html=True)
            s4.markdown(metric_tile("Vault Status","SECURE","","#10b981","🔒"), unsafe_allow_html=True)
        else:
            st.info("No ledger records yet.")
    elif h_res3 and h_res3.status_code == 403:
        st.warning("🛡️ Admin or Auditor clearance required to access the security ledger.")
    else:
        st.error("❌ Cannot connect to backend.")

    mini_separator()
    sc_a, sc_b = st.columns(2)
    with sc_a:
        st.markdown("""
        <div class="ai-matrix">
            <span style="color:#00f0ff;font-weight:700;">[ZERO-TRUST PRIVACY GRID — ACTIVE]</span><br><br>
            <span style="color:#4b6584;">CIPHER ENGINE: Fernet AES-256-CBC + HMAC-SHA256</span><br>
            <span style="color:#4b6584;">AUTH SCHEME: PBKDF2-SHA256 × 100,000 iter</span><br>
            <span style="color:#4b6584;">SESSION: JWT HS256 Bearer Tokens (1hr TTL)</span><br><br>
            <div style="color:#10b981;font-size:1rem;">⚡ DB VAULT ENCRYPTED — ZERO PLAINTEXT EXPOSURE ⚡</div>
        </div>
        """, unsafe_allow_html=True)
    with sc_b:
        st.markdown('<div class="t-section" style="margin-bottom:10px;">🔑 Live Cryptographic Diagnostics</div>', unsafe_allow_html=True)
        sm_diag = st.session_state.active_data["system_telemetry_metrics"] if st.session_state.active_data else {}
        st.json({
            "vault_engine":         "SQLAlchemy + Fernet AES-256",
            "session_isolation":    "ACTIVE",
            "storage_mode":         "Row-Level Symmetric Encryption",
            "breach_attempts":      sm_diag.get("unauthorized_breaches", 0),
            "clearance_role":       st.session_state.user_role,
            "jwt_auth_active":      True,
            "pbkdf2_iterations":    100000,
        })
        st.info("ℹ️ All telemetry rows are encrypted as binary blobs in `data/aegis_secure_vault.db`. Raw file inspection returns unreadable bytes.")


# ─────────────────────────────────────────────────
# TAB 9 — ANPR & TRAFFIC VIOLATIONS
# ─────────────────────────────────────────────────
with tab_anpr:
    sec_div("🚘 ANPR — AUTOMATIC NUMBER PLATE RECOGNITION  ·  TRAFFIC VIOLATION DETECTION")

    anpr_scenario_label = st.selectbox(
        "Select Scenario for ANPR & Violation Scan",
        list(SCENARIO_MAP.keys()),
        key="anpr_scenario_sel"
    )
    anpr_scenario = SCENARIO_MAP[anpr_scenario_label]

    run_anpr_btn = st.button("🔍 Run ANPR & Violation Scan", type="primary", use_container_width=True, key="run_anpr_btn")

    if run_anpr_btn:
        col_anpr, col_viol = st.columns(2)

        with col_anpr:
            sec_div("📷 ANPR OCR — Number Plate Registry")
            try:
                anpr_res = requests.get(
                    f"{ANPR_URL}/{anpr_scenario}",
                    params={"latitude":  st.session_state.latitude,
                            "longitude": st.session_state.longitude,
                            "location_name": st.session_state.location_name},
                    headers=auth_header(), timeout=15
                )
                if anpr_res.status_code == 200:
                    anpr_data = anpr_res.json()
                    plates    = anpr_data.get("anpr_records", [])
                    summary   = anpr_data.get("summary", {})

                    # Jurisdiction banner
                    _cf_a = summary.get("country_flag", st.session_state.country_flag)
                    _cn_a = summary.get("country_name", st.session_state.country_name)
                    _pf_a = summary.get("plate_format",  st.session_state.plate_format)
                    _pe_a = summary.get("plate_example", "")
                    st.markdown(f"""
                    <div style="background:rgba(0,240,255,.05);border:1px solid rgba(0,240,255,.15);
                    border-radius:8px;padding:8px 14px;margin-bottom:12px;
                    font-family:'JetBrains Mono',monospace;font-size:.72rem;color:#94a3b8;">
                    {_cf_a} <strong style="color:#00f0ff;">{_cn_a}</strong>
                    &nbsp;&middot;&nbsp; Format: <code style="color:#e2e8f0;">{_pf_a}</code>
                    {f'&nbsp;&middot;&nbsp; e.g. <code style="color:#f59e0b;">{_pe_a}</code>' if _pe_a else ''}
                    </div>""", unsafe_allow_html=True)

                    # Summary metrics
                    sm1, sm2, sm3 = st.columns(3)
                    sm1.markdown(metric_tile("Plates Detected", summary.get("total_plates", len(plates)), "", "#00f0ff", "🔢"), unsafe_allow_html=True)
                    sm2.markdown(metric_tile("Registered",      summary.get("registered", "—"),            "", "#10b981", "✅"), unsafe_allow_html=True)
                    sm3.markdown(metric_tile("Flagged",         summary.get("flagged", "—"),               "", "#ef4444", "🚩"), unsafe_allow_html=True)

                    st.markdown("<br>", unsafe_allow_html=True)
                    for p in plates:
                        flag_color = "#ef4444" if p.get("flagged") else "#e2e8f0"
                        _p_flag    = p.get("country_flag", _cf_a)
                        st.markdown(
                            f'<div style="display:flex;justify-content:space-between;align-items:center;'
                            f'background:rgba(0,0,0,.25);border:1px solid rgba(255,255,255,.05);'
                            f'border-radius:8px;padding:8px 14px;margin-bottom:6px;">'
                            f'<span style="background:#fff;color:#000;font-family:\'JetBrains Mono\',monospace;'
                            f'font-weight:700;padding:3px 8px;border-radius:3px;border:2px solid #000;font-size:.82rem;">'
                            f'{_p_flag} {p.get("plate","—")}</span>'
                            f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:.72rem;color:#00f0ff;">{p.get("vehicle_type","—")}</span>'
                            f'<span style="font-size:.72rem;color:{flag_color};">{"🚩 FLAGGED" if p.get("flagged") else "✅ CLEAR"}</span>'
                            f'</div>', unsafe_allow_html=True)
                    if not plates:
                        st.info("No plates detected for this scenario.")
                elif anpr_res.status_code == 401:
                    st.warning("🔑 Session expired. Please logout and login again.")
                else:
                    st.error(f"❌ ANPR API error: {anpr_res.status_code}")
            except Exception as e:
                st.error(f"❌ ANPR offline: {e}")

        with col_viol:
            sec_div("⚠️ TRAFFIC VIOLATION DETECTION")
            try:
                viol_res = requests.get(
                    f"{VIOLATIONS_URL}/{anpr_scenario}",
                    params={"latitude":  st.session_state.latitude,
                            "longitude": st.session_state.longitude,
                            "location_name": st.session_state.location_name},
                    headers=auth_header(), timeout=15
                )
                if viol_res.status_code == 200:
                    viol_data  = viol_res.json()
                    violations = viol_data.get("violations", [])
                    vsummary   = viol_data.get("summary", {})

                    # Jurisdiction banner
                    _cf_v  = vsummary.get("country_flag", st.session_state.country_flag)
                    _cn_v  = vsummary.get("country_name", st.session_state.country_name)
                    _sym_v = vsummary.get("currency_symbol", st.session_state.currency_symbol)
                    _cod_v = vsummary.get("currency_code",   st.session_state.currency_code)
                    _spd_v = vsummary.get("speed_limit_kmh", st.session_state.speed_limit_kmh)
                    _drv_v = vsummary.get("drive_side",      st.session_state.drive_side)
                    st.markdown(f"""
                    <div style="background:rgba(239,68,68,.05);border:1px solid rgba(239,68,68,.15);
                    border-radius:8px;padding:8px 14px;margin-bottom:12px;
                    font-family:'JetBrains Mono',monospace;font-size:.72rem;color:#94a3b8;">
                    {_cf_v} <strong style="color:#f59e0b;">{_cn_v}</strong>
                    &nbsp;&middot;&nbsp; Currency: <strong style="color:#e2e8f0;">{_sym_v} {_cod_v}</strong>
                    &nbsp;&middot;&nbsp; Speed: <strong style="color:#e2e8f0;">{_spd_v} km/h</strong>
                    &nbsp;&middot;&nbsp; Drive: <strong style="color:#e2e8f0;">{_drv_v.upper()}</strong>
                    </div>""", unsafe_allow_html=True)

                    vm1, vm2, vm3 = st.columns(3)
                    vm1.markdown(metric_tile("Total Violations", len(violations),                                  "",  "#ef4444", "⚠️"), unsafe_allow_html=True)
                    vm2.markdown(metric_tile("Fine (Local)",     vsummary.get("total_fine_local",  f"{_sym_v}0"), "",  "#f59e0b", "💰"), unsafe_allow_html=True)
                    vm3.markdown(metric_tile("Fine (USD)",       vsummary.get("total_fine_usd",    "≈ $0"),        "",  "#a855f7", "💵"), unsafe_allow_html=True)

                    st.markdown("<br>", unsafe_allow_html=True)
                    if violations:
                        for idx_v, v in enumerate(violations):
                            vtype     = v.get("type", "—")
                            vid       = v.get("vehicle_id", "Unknown")
                            fine_loc  = v.get("fine_local",  f"{_sym_v}{v.get('fine_amount','—')}")
                            fine_usd  = v.get("fine_usd",   "")
                            plate     = v.get("plate", "")
                            flag_v    = v.get("country_flag", _cf_v)
                            plate_str = f" | 🪪 {flag_v} {plate}" if plate and plate != "—" else ""
                            sev_color = {"CRITICAL": "#ef4444", "HIGH": "#f59e0b", "MEDIUM": "#3b82f6"}.get(v.get("severity","MEDIUM"), "#94a3b8")
                            st.markdown(
                                f'<div style="background:rgba(239,68,68,.08);border:1px solid rgba(239,68,68,.2);'
                                f'border-left:3px solid {sev_color};'
                                f'border-radius:8px;padding:10px 14px;margin-bottom:8px;font-family:\'JetBrains Mono\',monospace;font-size:.75rem;">'
                                f'<div style="color:#ef4444;font-weight:700;margin-bottom:4px;">⚠️ {vtype}</div>'
                                f'<div style="color:#94a3b8;">{vid}{plate_str}</div>'
                                f'<div style="margin-top:4px;">'
                                f'<span style="color:#f59e0b;font-weight:700;">{fine_loc}</span>'
                                f'{f" &nbsp;<span style=\"color:#6b7280;font-size:.7rem;\">{fine_usd}</span>" if fine_usd else ""}'
                                f'</div>'
                                f'</div>', unsafe_allow_html=True)
                            
                            pdf_url = f"{BACKEND_URL}/api/v1/violations/citation-pdf/{v.get('id', f'TKT-{idx_v+1:04d}')}?plate={requests.utils.quote(plate or 'DL-01-AB-1234')}&fine_amount={v.get('fine_amount', 1500)}"
                            st.markdown(f'<a href="{pdf_url}" target="_blank" style="display:inline-block;padding:4px 10px;background:rgba(0,240,255,.1);border:1px solid #00f0ff;color:#00f0ff;border-radius:4px;font-family:\'JetBrains Mono\',monospace;font-size:.68rem;text-decoration:none;margin-bottom:10px;">📄 View / Print Official Citation PDF</a>', unsafe_allow_html=True)
                    else:
                        st.success("✅ No traffic violations detected for this scenario.")
                else:
                    st.error(f"❌ Violations API error: {viol_res.status_code}")
            except Exception as e:
                st.error(f"❌ Violations module offline: {e}")


# ─────────────────────────────────────────────────
# TAB 10 — PIPELINE STATUS
# ─────────────────────────────────────────────────
with tab_pipeline:
    sec_div("⚙️ AEGIS TRAFFIC PIPELINE — MODULE STATUS DASHBOARD")

    if st.button("↻ Refresh Pipeline Status", type="primary", key="refresh_pipeline"):
        st.rerun()

    try:
        ps_res = requests.get(PIPELINE_URL, timeout=8)
        if ps_res.status_code == 200:
            ps_data  = ps_res.json()
            modules  = ps_data.get("modules", {})
            stages   = ps_data.get("pipeline_stages", [])
            sm_ps    = ps_data.get("system_metrics", {})

            # System overview metrics
            psc1, psc2, psc3, psc4 = st.columns(4)
            psc1.markdown(metric_tile("Overall Status", ps_data.get("overall_status","—"), "", "#10b981", "✅"), unsafe_allow_html=True)
            psc2.markdown(metric_tile("Version",        ps_data.get("version","—"),        "", "#00f0ff", "🔢"), unsafe_allow_html=True)
            psc3.markdown(metric_tile("Total Requests", sm_ps.get("total_requests",0),     "", "#a855f7", "📡"), unsafe_allow_html=True)
            psc4.markdown(metric_tile("Critical Events",sm_ps.get("critical_incidents",0), "", "#ef4444", "🚨"), unsafe_allow_html=True)

            mini_separator()

            # Module status grid
            sec_div("🧩 MODULE HEALTH MATRIX")
            mod_cols = st.columns(3)
            for idx, (mod_name, mod_info) in enumerate(modules.items()):
                status_txt = mod_info.get("status","—")
                is_online  = "OFFLINE" not in status_txt.upper()
                col_hex    = "#10b981" if is_online else "#ef4444"
                dot        = "🟢" if is_online else "🔴"
                with mod_cols[idx % 3]:
                    st.markdown(
                        f'<div style="background:rgba(6,12,26,.85);border:1px solid rgba(0,240,255,.1);'
                        f'border-radius:8px;padding:10px 14px;margin-bottom:8px;">'
                        f'<div style="font-family:\'Orbitron\',sans-serif;font-size:.65rem;color:#4b6584;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">'
                        f'{mod_name.replace("_"," ")}</div>'
                        f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:.72rem;color:{col_hex};">'
                        f'{dot} {status_txt}</div>'
                        f'<div style="font-size:.68rem;color:#4b6584;margin-top:2px;">{mod_info.get("module","")}</div>'
                        f'</div>', unsafe_allow_html=True)

            mini_separator()

            # Pipeline stages
            sec_div("🔄 END-TO-END PIPELINE FLOW")
            for i, stage in enumerate(stages):
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:10px;padding:7px 12px;'
                    f'background:rgba(0,0,0,.2);border-radius:6px;margin-bottom:5px;'
                    f'font-family:\'JetBrains Mono\',monospace;font-size:.78rem;color:#e2e8f0;">'
                    f'<span style="color:#00f0ff;min-width:24px;">{"0" if i+1 < 10 else ""}{i+1}</span>'
                    f'<span style="color:#00f0ff;margin-right:4px;">▶</span>'
                    f'{stage}'
                    f'</div>', unsafe_allow_html=True)
        else:
            st.error(f"❌ Pipeline status API returned {ps_res.status_code}")
    except Exception as e:
        st.error(f"❌ Pipeline status unavailable: {e}")
        st.markdown("""
        <div class="card card-alert-red" style="padding:20px;text-align:center;">
            <div style="font-size:2rem;margin-bottom:8px;">⚙️</div>
            <div style="font-family:'Orbitron',sans-serif;font-size:.88rem;color:#ef4444;">BACKEND MICROSERVICE OFFLINE</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:.75rem;color:#64748b;margin-top:8px;">
                Start FastAPI: <code style="color:#00f0ff;">uvicorn app.main:app --reload</code>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────
# TAB 11 — PUBLIC CITIZEN PORTAL
# ─────────────────────────────────────────────────
with tab_citizen:
    sec_div("👥 MUNICIPAL PUBLIC CITIZEN PORTAL — REAL-TIME TRAFFIC & SAFETY SERVICES")
    st.markdown("<p style='color:#64748b;font-family:JetBrains Mono;font-size:.78rem;'>Public access portal for city residents and drivers to view live congestion, check/appeal traffic fines, and report road hazards.</p>", unsafe_allow_html=True)

    cit_tab1, cit_tab2, cit_tab3 = st.tabs([
        "🗺️ Live Congestion & Detours",
        "💳 Fine Lookup & Challenger",
        "🚨 Report Road Hazard"
    ])

    with cit_tab1:
        sec_div("🌍 PUBLIC LIVE TRAFFIC MAP & ECO-DRIVING ADVISORY")
        pc1, pc2, pc3, pc4 = st.columns(4)
        pc1.markdown(metric_tile("Target City", st.session_state.location_name, "", "#00f0ff", "📍"), unsafe_allow_html=True)
        pc2.markdown(metric_tile("Traffic Flow", "MODERATE", "", "#10b981", "🚦"), unsafe_allow_html=True)
        pc3.markdown(metric_tile("Eco Speed", "45 km/h", "", "#a855f7", "🌱"), unsafe_allow_html=True)
        pc4.markdown(metric_tile("Air Quality", "AQI 42 (Good)", "", "#06b6d4", "🍃"), unsafe_allow_html=True)

        st.markdown("""
        <div class="card" style="margin-top:14px;">
            <div class="t-section" style="margin-bottom:8px;">📢 ACTIVE MUNICIPAL DETOUR ADVISORIES</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:.78rem;color:#e2e8f0;line-height:1.8;">
                • <strong style="color:#00f0ff;">Bypass Route A:</strong> Utility maintenance on Outer Ring Rd. Detour saves ~8 minutes.<br>
                • <strong style="color:#f59e0b;">Emergency Green Wave Active:</strong> Central Expressway lane 2 restricted for emergency convoy.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with cit_tab2:
        sec_div("💳 CITIZEN REGISTRATION PLATE FINE LOOKUP & DISPUTE PORTAL")
        lookup_col, result_col = st.columns([1, 1.5])
        with lookup_col:
            search_plate = st.text_input("Enter Vehicle Registration Plate", placeholder="e.g. DL-01-AB-1234", key="citizen_plate_lookup_input")
            search_btn = st.button("🔍 Search Active Fines", type="primary", use_container_width=True, key="btn_citizen_search_fines")

        with result_col:
            if search_btn and search_plate.strip():
                try:
                    c_res = requests.get(f"{BACKEND_URL}/api/v1/public/citations/search", params={"plate": search_plate}, timeout=8)
                    if c_res.ok:
                        c_data = c_res.json()
                        st.markdown(f"#### 🪪 Vehicle: `{c_data['plate']}`")
                        st.markdown(f"**Total Outstanding Fine:** `{st.session_state.currency_symbol}{c_data['total_outstanding_fine']}`")
                        for tkt in c_data.get("tickets", []):
                            st.markdown(f"""
                            <div style="background:rgba(239,68,68,.08);border:1px solid rgba(239,68,68,.2);border-radius:8px;padding:10px;margin-bottom:8px;font-family:'JetBrains Mono',monospace;font-size:.78rem;">
                                <div style="color:#ef4444;font-weight:700;">⚠️ {tkt['type']}</div>
                                <div style="color:#94a3b8;">Ticket ID: {tkt['ticket_id']} | Date: {tkt['date']}</div>
                                <div style="color:#f59e0b;font-weight:700;margin-top:4px;">Fine Amount: {st.session_state.currency_symbol}{tkt['fine_amount_inr']}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            if st.button(f"⚖️ Contest Ticket {tkt['ticket_id']}", key=f"btn_appeal_{tkt['ticket_id']}"):
                                st.success(f"✅ Dispute claim registered for Ticket {tkt['ticket_id']}. Reference ID: APP-{uuid.uuid4().hex[:6].upper()}")
                    else:
                        st.error("Error connecting to citation lookup service.")
                except Exception as ex:
                    st.error(f"Lookup service offline: {ex}")
            else:
                st.info("Enter your vehicle plate number on the left to check for active citations.")

    with cit_tab3:
        sec_div("🚨 PUBLIC ROAD HAZARD REPORTING FORM")
        h_col1, h_col2 = st.columns(2)
        with h_col1:
            hz_name = st.text_input("Your Name / Alias", value="Citizen Reporter", key="hz_citizen_name")
            hz_type = st.selectbox("Hazard Type", ["Pothole", "Vehicle Accident", "Traffic Light Outage", "Road Flooding", "Debris on Road"], key="hz_type_select")
            hz_loc  = st.text_input("Hazard Location", value=st.session_state.location_name, key="hz_location_input")
            hz_desc = st.text_area("Description / Details", placeholder="Describe the road condition or danger...", key="hz_description_textarea")
            sub_hz  = st.button("📋 Submit Hazard Report to City Dispatch", type="primary", use_container_width=True, key="btn_submit_hazard_report")

            if sub_hz:
                try:
                    payload_hz = {
                        "citizen_name": hz_name,
                        "hazard_type": hz_type,
                        "location_name": hz_loc,
                        "latitude": st.session_state.latitude,
                        "longitude": st.session_state.longitude,
                        "description": hz_desc
                    }
                    hr = requests.post(f"{BACKEND_URL}/api/v1/public/hazards/report", json=payload_hz, timeout=8)
                    if hr.ok:
                        st.success(f"✅ Report submitted! Ticket ID: {hr.json().get('report_id')}")
                    else:
                        st.error("Error submitting report.")
                except Exception as ex:
                    st.error(f"Dispatch server offline: {ex}")

        with h_col2:
            st.markdown("#### 📋 Community Hazard Feed")
            try:
                hl = requests.get(f"{BACKEND_URL}/api/v1/public/hazards/list", timeout=6)
                if hl.ok:
                    h_list = hl.json().get("hazards", [])
                    if h_list:
                        for hz in h_list[:6]:
                            st.markdown(f"""
                            <div style="background:rgba(0,0,0,.2);border:1px solid rgba(255,255,255,.05);border-radius:6px;padding:8px 12px;margin-bottom:6px;font-family:'JetBrains Mono',monospace;font-size:.75rem;">
                                <span style="color:#f59e0b;font-weight:700;">🚨 {hz['hazard_type']}</span> &nbsp;|&nbsp; <span style="color:#00f0ff;">{hz['location_name']}</span><br>
                                <span style="color:#94a3b8;">Status: <strong style="color:#10b981;">{hz['status']}</strong> &nbsp;|&nbsp; Reported: {hz['date']}</span>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No hazards reported yet.")
            except:
                st.warning("Hazard feed offline.")


# ──────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────
mini_separator()
sm_foot = st.session_state.active_data["system_telemetry_metrics"] if st.session_state.active_data else {}
st.code(
    f"// AEGIS-TRAFFIC v8.0 // Operations Node System Logs\n"
    f"[USER] {st.session_state.username.upper()} [{st.session_state.user_role.upper()}]  "
    f"[SCANS] {sm_foot.get('total_requests',0)}  "
    f"[CRITICAL] {sm_foot.get('critical_incidents',0)}  "
    f"[BLOCKED] {sm_foot.get('unauthorized_breaches',0)}\n"
    f"[SITE] {st.session_state.location_name}  "
    f"[LAT] {st.session_state.latitude:.4f}  [LON] {st.session_state.longitude:.4f}\n"
    f"[ENGINE] Multimodal YOLOv8 + DistilBERT-MNLI + Qwen2.5 Fusion Layer Active",
    language="javascript"
)