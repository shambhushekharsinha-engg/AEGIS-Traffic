"""
AEGIS-Traffic — Reusable UI Components & Widgets
"""
import streamlit as st

def risk_color(risk: float) -> str:
    """Returns color hex based on risk level percentage."""
    if risk > 70:
        return "#ef4444"
    if risk > 35:
        return "#f59e0b"
    return "#10b981"

def metric_tile(label: str, value: str, unit: str = "", color: str = "#00f0ff", icon: str = "") -> str:
    """Renders glassmorphic metric tile HTML snippet."""
    return f"""
    <div class="metric-tile">
        <div class="label">{icon} {label}</div>
        <div class="value" style="color:{color};">{value}<span class="unit">{unit}</span></div>
    </div>"""

def sec_div(text: str):
    """Renders section divider with neon cyan accent."""
    st.markdown(f'<div class="sec-div">{text}</div>', unsafe_allow_html=True)

def mini_separator():
    """Renders clean horizontal divider."""
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

def render_login_portal(client, on_login_success):
    """Renders full login/registration modal portal."""
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

            col_q1, col_q2, col_q3 = st.columns(3)
            if col_q1.button("🔑 Admin Quick Entry", use_container_width=True, key="btn_quick_admin"):
                st.session_state.quick_user = "admin"
                st.session_state.quick_pass = "Admin@AEGIS2024!"
                st.rerun()
            if col_q2.button("🔑 Operator Quick Entry", use_container_width=True, key="btn_quick_operator"):
                st.session_state.quick_user = "operator"
                st.session_state.quick_pass = "Operator@AEGIS2024!"
                st.rerun()
            if col_q3.button("🔑 Auditor Quick Entry", use_container_width=True, key="btn_quick_auditor"):
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
                        try:
                            res = client.login(username, password)
                            st.session_state.jwt_token = res["access_token"]
                            st.session_state.user_role = res["role"]
                            st.session_state.username = res["username"]
                            st.success("✅ Authentication successful. Initializing dashboard...")
                            st.rerun()
                        except Exception as e:
                            st.error(f"🚫 {e}")

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
                        try:
                            client.register(reg_user, reg_pass, reg_role)
                            st.success(f"✅ {reg_user} registered as {reg_role}. Login to access.")
                        except Exception as e:
                            st.error(f"❌ {e}")
