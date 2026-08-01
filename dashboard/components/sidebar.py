"""
AEGIS-Traffic — Sidebar Navigation Component
"""
import streamlit as st

def render_sidebar():
    """Renders sidebar navigation controls, system scenario selector, and mode controls."""
    with st.sidebar:
        st.markdown("""
        <div style="padding:16px 12px 8px;">
            <div class="t-hero" style="font-size:1.2rem;">AEGIS CORE</div>
            <div class="t-sub">INTELLIGENT COMMAND HUB</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.session_state.current_page = st.radio(
            "SYSTEM MODULES",
            [
                "📊 Operations HUD",
                "📈 Predictive Analytics",
                "🌍 Map Intelligence",
                "🤖 AI Copilot",
                "🚘 ANPR & Violations",
                "📑 Reports & Exports",
                "👥 Public Citizen Portal",
                "📚 Learning Guide",
                "🛡️ Audit & Security",
                "⚙️ Settings & Pipeline"
            ],
            index=0,
            key="sidebar_navigation_radio"
        )
        
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.markdown('<div class="t-section" style="font-size:.72rem;margin-bottom:8px;padding-left:12px;">SIMULATION & OVERRIDE</div>', unsafe_allow_html=True)
        
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
