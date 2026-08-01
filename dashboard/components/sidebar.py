"""
AEGIS-Traffic — Sidebar Navigation Component (3D Button Engine)
"""
import streamlit as st

MODULE_LIST = [
    ("📊 Operations HUD", "📊 Operations HUD"),
    ("📈 Predictive Analytics", "📈 Predictive Analytics"),
    ("🌍 Map Intelligence", "🌍 Map Intelligence"),
    ("🤖 AI Copilot", "🤖 AI Copilot"),
    ("🚘 ANPR & Violations", "🚘 ANPR & Violations"),
    ("📑 Reports & Exports", "📑 Reports & Exports"),
    ("👥 Public Citizen Portal", "👥 Public Citizen Portal"),
    ("📚 Learning Guide", "📚 Learning Guide"),
    ("🛡️ Audit & Security", "🛡️ Audit & Security"),
    ("⚙️ Settings & Pipeline", "⚙️ Settings & Pipeline")
]


def render_sidebar():
    """Renders sidebar 3D module navigation buttons, scenario selector, and mode controls."""
    with st.sidebar:
        st.markdown("""
        <div style="padding:12px 8px 4px;">
            <div class="t-hero" style="font-size:1.3rem;">AEGIS CORE</div>
            <div class="t-sub" style="font-size:.68rem;">INTELLIGENT COMMAND HUB</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="t-section" style="font-size:.78rem;margin:10px 0 8px 4px;color:#00f0ff;letter-spacing:2px;">⚡ SYSTEM MODULES</div>', unsafe_allow_html=True)

        current = st.session_state.get("current_page", MODULE_LIST[0][0])

        # Render explicit 3D navigation buttons in the sidebar
        for page_name, display_name in MODULE_LIST:
            is_active = (page_name == current)
            btn_label = f"▶  {display_name}" if is_active else f"   {display_name}"

            if st.button(btn_label, key=f"sb_3d_btn_{display_name}", use_container_width=True):
                st.session_state.current_page = page_name
                st.rerun()

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.markdown('<div class="t-section" style="font-size:.72rem;margin-bottom:8px;padding-left:4px;">SIMULATION & OVERRIDE</div>', unsafe_allow_html=True)

        st.session_state.active_scenario = st.selectbox(
            "TRAFFIC SCENARIO",
            [
                "🟢 Normal Flowing Traffic",
                "🟡 Congested Traffic Queues",
                "🚨 Emergency Vehicle Incoming",
                "💥 Vehicle Collision Accident",
                "🛡️ Camera Feed Tampered"
            ],
            key="sb_scenario_select"
        )

        st.session_state.active_mode = st.selectbox(
            "OPERATIONAL MODE",
            [
                "AI Automated Fusion",
                "Manual Override",
                "Security Lockdown",
                "Predictive Optimization"
            ],
            key="sb_mode_select"
        )

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.markdown("""
        <div class="sb-block">
            <div class="sb-label">LATENCY & INFRASTRUCTURE</div>
            <div style="color:#00f0ff;font-weight:700;margin-top:4px;">12ms // EDGE NODE OK</div>
        </div>
        """, unsafe_allow_html=True)
