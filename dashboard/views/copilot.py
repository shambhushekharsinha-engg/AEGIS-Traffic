"""
AEGIS-Traffic — AI Copilot Assistant Page Module
"""
import streamlit as st
from dashboard.components.widgets import sec_div


def render_copilot_page(client):
    """Renders interactive AI Assistant chat for municipal traffic operators."""
    sec_div("🤖 AEGIS AI TRAFFIC COPILOT — INTERACTIVE ASSISTANT")

    if "copilot_history" not in st.session_state:
        st.session_state.copilot_history = [
            {"role": "assistant", "content": "Hello Operator! I am AEGIS AI Copilot. How can I assist with traffic flow optimization or emergency dispatch today?"}
        ]

    for msg in st.session_state.copilot_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-msg-user">👤 <strong>Operator:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-msg-ai">🤖 <strong>AEGIS AI:</strong> {msg["content"]}</div>', unsafe_allow_html=True)

    prompt = st.chat_input("Ask AI Copilot (e.g. 'Recommend signal timing for heavy congestion on North Corridor')...")
    if prompt:
        st.session_state.copilot_history.append({"role": "user", "content": prompt})
        token = st.session_state.get("jwt_token", "")
        with st.spinner("AI Copilot analyzing sensor telemetry..."):
            reply_obj = client.chat_copilot(prompt, token)
            reply = reply_obj.get("reply", "Received and processed operational query.")
        st.session_state.copilot_history.append({"role": "assistant", "content": reply})
        st.rerun()
