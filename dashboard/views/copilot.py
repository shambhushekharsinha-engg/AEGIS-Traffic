"""
AEGIS-Traffic — AI Copilot Assistant Page Module
"""

import streamlit as st

from dashboard.components.widgets import sec_div


def render_copilot_page(client):
    """Renders interactive AI Assistant chat for municipal traffic operators."""
    sec_div("🤖 AEGIS AI TRAFFIC COPILOT — INTERACTIVE ASSISTANT")

    st.markdown(
        """
    <div style="background: linear-gradient(90deg, rgba(168,85,247,0.1), rgba(0,240,255,0.1)); border: 1px solid rgba(0,240,255,0.3); padding: 15px 20px; border-radius: 8px; margin-bottom: 20px; display: flex; align-items: center; gap: 15px; box-shadow: 0 0 15px rgba(0, 240, 255, 0.05);">
        <div style="font-size: 2.5rem; text-shadow: 0 0 10px rgba(0,240,255,0.8);">🧠</div>
        <div>
            <div style="font-family: 'Orbitron', sans-serif; font-size: 1.1rem; font-weight: 700; color: #00f0ff; letter-spacing: 1px;">QWEN 2.5 TRAFFIC INTELLIGENCE</div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #94a3b8; margin-top: 4px;">NATURAL LANGUAGE OPERATIONAL QUERY SYSTEM • ENCRYPTED SESSION</div>
        </div>
    </div>
    
    <style>
    /* Chat Bubble Animations and Glows */
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    .cyber-chat-user {
        background: linear-gradient(135deg, rgba(0, 240, 255, 0.15) 0%, rgba(0, 240, 255, 0.05) 100%);
        border: 1px solid rgba(0, 240, 255, 0.4);
        border-right: 4px solid #00f0ff;
        border-radius: 12px 0px 12px 12px;
        padding: 12px 16px;
        margin: 10px 0 10px auto;
        max-width: 80%;
        color: #e2e8f0;
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        line-height: 1.5;
        box-shadow: 0 4px 12px rgba(0, 240, 255, 0.1);
        animation: slideInRight 0.3s ease-out forwards;
    }
    
    .cyber-chat-ai {
        background: linear-gradient(135deg, rgba(168, 85, 247, 0.15) 0%, rgba(168, 85, 247, 0.05) 100%);
        border: 1px solid rgba(168, 85, 247, 0.4);
        border-left: 4px solid #a855f7;
        border-radius: 0px 12px 12px 12px;
        padding: 12px 16px;
        margin: 10px auto 10px 0;
        max-width: 80%;
        color: #e2e8f0;
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        line-height: 1.5;
        box-shadow: 0 4px 12px rgba(168, 85, 247, 0.1);
        animation: slideInLeft 0.3s ease-out forwards;
    }
    
    .chat-avatar {
        display: inline-block;
        width: 24px;
        height: 24px;
        text-align: center;
        line-height: 24px;
        border-radius: 50%;
        margin-right: 8px;
        font-size: 0.8rem;
    }
    .avatar-user { background: rgba(0, 240, 255, 0.2); border: 1px solid #00f0ff; color: #00f0ff; }
    .avatar-ai { background: rgba(168, 85, 247, 0.2); border: 1px solid #a855f7; color: #a855f7; }
    
    .chat-timestamp {
        display: block;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem;
        color: #64748b;
        margin-top: 8px;
        text-align: right;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    if "copilot_history" not in st.session_state:
        st.session_state.copilot_history = [
            {
                "role": "assistant",
                "content": "Hello Operator! I am AEGIS AI Copilot. I have full read-access to the municipal sensor grid. How can I assist with traffic flow optimization or emergency dispatch today?",
            }
        ]

    for msg in st.session_state.copilot_history:
        if msg["role"] == "user":
            st.markdown(
                f"""
            <div class="cyber-chat-user">
                <div style="display:flex; align-items:center; margin-bottom:6px; font-family:'Orbitron',sans-serif; font-size:0.75rem; color:#00f0ff;">
                    <span class="chat-avatar avatar-user">OP</span> COMMAND AUTHORITY
                </div>
                {msg["content"]}
            </div>
            """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
            <div class="cyber-chat-ai">
                <div style="display:flex; align-items:center; margin-bottom:6px; font-family:'Orbitron',sans-serif; font-size:0.75rem; color:#a855f7;">
                    <span class="chat-avatar avatar-ai">AI</span> AEGIS COPILOT
                </div>
                {msg["content"]}
            </div>
            """,
                unsafe_allow_html=True,
            )

    prompt = st.chat_input(
        "Ask AI Copilot (e.g. 'Recommend signal timing for heavy congestion on North Corridor')..."
    )
    if prompt:
        st.session_state.copilot_history.append({"role": "user", "content": prompt})
        token = st.session_state.get("jwt_token", "")
        with st.spinner(
            "🧠 AI Copilot fusing multimodal telemetry and generating tactical response..."
        ):
            reply_obj = client.chat_copilot(prompt, token)
            reply = reply_obj.get("reply", "Received and processed operational query.")
        st.session_state.copilot_history.append({"role": "assistant", "content": reply})
        st.rerun()
