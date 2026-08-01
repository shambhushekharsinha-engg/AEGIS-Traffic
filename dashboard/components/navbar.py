"""
AEGIS-Traffic — Top Navigation Bar Component
"""
import streamlit as st

def render_navbar(client):
    """Renders top header layout with system status, active user badge, and logout."""
    hcol1, hcol2, hcol3 = st.columns([2, 3, 2])
    with hcol1:
        st.markdown("""
        <div style="padding:8px 0;">
            <div class="t-hero">🚦 AEGIS-TRAFFIC</div>
            <div class="t-sub">SMART CITY AI OPERATIONS HUB</div>
        </div>
        """, unsafe_allow_html=True)
    with hcol2:
        flag = st.session_state.get("country_flag", "🇮🇳")
        country = st.session_state.get("country_name", "India")
        loc = st.session_state.get("location_name", "New Delhi")
        curr = st.session_state.get("currency_symbol", "₹")
        limit = st.session_state.get("speed_limit_kmh", 50)
        side = st.session_state.get("drive_side", "left")

        st.markdown(f"""
        <div style="background:rgba(6,12,26,.8);border:1px solid rgba(0,240,255,.15);border-radius:10px;padding:8px 14px;margin-top:6px;display:flex;align-items:center;justify-content:space-around;font-family:'JetBrains Mono',monospace;font-size:.72rem;">
            <div><span style="font-size:1.1rem;">{flag}</span> <strong style="color:#00f0ff;">{country}</strong></div>
            <div style="color:#64748b;">|</div>
            <div style="color:#94a3b8;">📍 {loc[:24]}...</div>
            <div style="color:#64748b;">|</div>
            <div>⚡ <span style="color:#38bdf8;">{limit} km/h</span></div>
            <div style="color:#64748b;">|</div>
            <div>🚗 <span style="color:#a855f7;">{side.upper()}</span></div>
        </div>
        """, unsafe_allow_html=True)
    with hcol3:
        user = st.session_state.get("username", "Operator")
        role = st.session_state.get("user_role", "Operator")
        
        is_alive = client.is_alive()
        status_dot = "🟢 ONLINE" if is_alive else "🔴 OFFLINE"
        
        st.markdown(f"""
        <div style="text-align:right;padding-top:10px;">
            <span style="font-family:'JetBrains Mono',monospace;font-size:.7rem;color:#10b981;margin-right:10px;">{status_dot}</span>
            <span class="badge-pill" style="margin-right:8px;">👤 {user} ({role})</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚪 LOGOUT", key="btn_global_logout"):
            for key in ["jwt_token", "user_role", "username"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
