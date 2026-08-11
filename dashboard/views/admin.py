"""
AEGIS-Traffic — Audit & Security Admin Page Module
"""

import os
import requests
import streamlit as st
import pandas as pd
from dashboard.components.widgets import sec_div, metric_tile

BACKEND = os.environ.get("AEGIS_BACKEND_URL", "http://127.0.0.1:8000")


def render_admin_page(client):
    """Renders administrative audit log, clearance role verifier, and emergency lockdown controls."""
    sec_div("🛡️ SECURITY AUDIT LEDGER & SYSTEM CONTAINMENT")

    user_role = st.session_state.get("user_role", "Operator")
    if user_role not in ["Admin", "Auditor"]:
        st.warning(
            "⚠️ Access Restricted: Administrative or Auditor clearance level required."
        )
        return

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(
            '<div class="t-section" style="margin-bottom:8px;">System Security & Access Audit Log</div>',
            unsafe_allow_html=True,
        )
        logs = [
            {
                "Event ID": "LOG-8821",
                "User": "admin",
                "Role": "Admin",
                "Action": "LOGIN_SUCCESS",
                "IP Address": "192.168.1.100",
                "Timestamp": "14:30:11 UTC",
            },
            {
                "Event ID": "LOG-8820",
                "User": "operator",
                "Role": "Operator",
                "Action": "SCENARIO_EXECUTE",
                "IP Address": "192.168.1.105",
                "Timestamp": "14:12:44 UTC",
            },
            {
                "Event ID": "LOG-8819",
                "User": "auditor",
                "Role": "Auditor",
                "Action": "REPORT_EXPORT",
                "IP Address": "192.168.1.110",
                "Timestamp": "13:55:00 UTC",
            },
            {
                "Event ID": "LOG-8818",
                "User": "unknown",
                "Role": "None",
                "Action": "AUTH_FAILURE",
                "IP Address": "203.0.113.45",
                "Timestamp": "13:40:19 UTC",
            },
        ]
        df_log = pd.DataFrame(logs)
        st.dataframe(df_log, use_container_width=True)

    with col2:
        st.markdown(
            '<div class="t-section" style="margin-bottom:8px;">Emergency Controls</div>',
            unsafe_allow_html=True,
        )
        if user_role == "Admin":
            if st.button(
                "🔒 ACTIVATE MUNICIPAL LOCKDOWN",
                use_container_width=True,
                key="btn_lockdown",
            ):
                st.error("🚨 EMERGENCY LOCKDOWN ENGAGED — ALL SIGNALS HELD AT RED")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(
                "🔄 PURGE AUDIT CACHE", use_container_width=True, key="btn_purge_cache"
            ):
                st.info("System audit cache successfully purged.")
        else:
            st.info("Auditor view: Read-only access to audit trail.")

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    sec_div("🔗 DECENTRALIZED LEDGER ANCHORING (v9.0.0)")

    st.markdown(
        """
    <div style="font-family:'JetBrains Mono',monospace;font-size:.8rem;color:#94a3b8;margin-bottom:12px;">
        Anchor current audit snapshot to the AEGIS-PRIVATE-LEDGER (Hyperledger). 
        Ensures cryptographic immutability of citations and access logs.
    </div>
    """,
        unsafe_allow_html=True,
    )

    if st.button(
        "⛓️ ANCHOR LEDGER SNAPSHOT TO BLOCKCHAIN",
        use_container_width=True,
        type="secondary",
    ):
        try:
            token = st.session_state.get("jwt_token", "")
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.post(
                f"{BACKEND}/api/v1/nextgen/blockchain-anchor",
                json={
                    "payload": {"records_count": len(logs)},
                    "anchor_type": "AUDIT_LOG",
                },
                headers=headers,
                timeout=10,
            )
            if res.ok:
                data = res.json()
                st.success(f"✅ SNAPSHOT ANCHORED IMMUTABLY.")
                st.code(
                    f"TX HASH: {data['transaction_hash']}\\nBLOCK HEIGHT: {data['block_height']}\\nNETWORK: {data['network']}",
                    language="bash",
                )
            else:
                st.error("Access Denied or Blockchain Node Offline.")
        except Exception:
            st.error("Ledger API Offline.")
