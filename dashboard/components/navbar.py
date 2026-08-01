"""
AEGIS-Traffic — Top Navigation Bar & 3D Module Tab System Component
"""
import streamlit as st

MODULE_PAGES = [
    ("📊 Operations HUD", "HUD"),
    ("📈 Predictive Analytics", "Analytics"),
    ("🌍 Map Intelligence", "GIS Map"),
    ("🤖 AI Copilot", "Copilot"),
    ("🚘 ANPR & Violations", "ANPR & Viols"),
    ("📑 Reports & Exports", "Reports"),
    ("👥 Public Citizen Portal", "Citizen"),
    ("📚 Learning Guide", "Guide"),
    ("🛡️ Audit & Security", "Admin"),
    ("⚙️ Settings & Pipeline", "Settings"),
]


def render_navbar(client):
    """Renders top header layout, status badges, and right-aligned 3D module tab bar."""
    hcol1, hcol2, hcol3 = st.columns([2, 3, 2.5])
    with hcol1:
        st.markdown("""
        <div style="padding:4px 0;">
            <div class="t-hero" style="font-size:1.5rem;">🚦 AEGIS-TRAFFIC</div>
            <div class="t-sub" style="font-size:.7rem;">SMART CITY AI OPERATIONS HUB</div>
        </div>
        """, unsafe_allow_html=True)
    with hcol2:
        flag = st.session_state.get("country_flag", "🇮🇳")
        country = st.session_state.get("country_name", "India")
        loc = st.session_state.get("location_name", "New Delhi")
        limit = st.session_state.get("speed_limit_kmh", 50)
        side = st.session_state.get("drive_side", "left")

        st.markdown(f"""
        <div style="background:rgba(6,12,26,.85);border:1px solid rgba(0,240,255,.2);border-radius:10px;padding:6px 14px;margin-top:2px;display:flex;align-items:center;justify-content:space-around;font-family:'JetBrains Mono',monospace;font-size:.72rem;box-shadow:0 4px 15px rgba(0,0,0,0.5);">
            <div><span style="font-size:1.1rem;">{flag}</span> <strong style="color:#00f0ff;">{country}</strong></div>
            <div style="color:#64748b;">|</div>
            <div style="color:#94a3b8;">📍 {loc[:20]}...</div>
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
        
        c_status, c_logout = st.columns([2, 1])
        with c_status:
            st.markdown(f"""
            <div style="text-align:right;padding-top:4px;">
                <span style="font-family:'JetBrains Mono',monospace;font-size:.68rem;color:#10b981;margin-right:8px;">{status_dot}</span>
                <span class="badge-pill">👤 {user} ({role})</span>
            </div>
            """, unsafe_allow_html=True)
        with c_logout:
            if st.button("🚪 LOGOUT", key="btn_global_logout", use_container_width=True):
                for key in ["jwt_token", "user_role", "username"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

    # ── RIGHT-ALIGNED 3D MODULE TABS BAR ──
    st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)
    
    current = st.session_state.get("current_page", "📊 Operations HUD")
    
    # Render 3D Navigation Tab Buttons across columns aligned right
    cols = st.columns(len(MODULE_PAGES))
    for col, (page_name, short_label) in zip(cols, MODULE_PAGES):
        is_active = (page_name == current)
        btn_label = f"✨ {short_label}" if is_active else short_label
        
        if col.button(btn_label, key=f"nav_tab_{short_label}", use_container_width=True):
            st.session_state.current_page = page_name
            st.rerun()
