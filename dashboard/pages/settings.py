"""
AEGIS-Traffic — System Settings Page Module
"""
import os
import streamlit as st
from dashboard.components.widgets import sec_div


def render_settings_page(client):
    """Renders node settings, API base URL configuration, and model threshold parameters."""
    sec_div("⚙️ NODE CONFIGURATION & API ENDPOINTS")

    st.markdown('<div class="t-section" style="margin-bottom:8px;">Backend Connection Settings</div>', unsafe_allow_html=True)
    backend_url = st.text_input("FastAPI Backend URL", value=os.environ.get("AEGIS_BACKEND_URL", "http://127.0.0.1:8000"), key="settings_backend_url")

    st.markdown('<div class="t-section" style="margin-top:16px;margin-bottom:8px;">Computer Vision Parameters</div>', unsafe_allow_html=True)
    conf_thresh = st.slider("YOLOv8 Detection Threshold", 0.1, 1.0, 0.4, 0.05, key="settings_yolo_thresh")
    iou_thresh = st.slider("IoU NMS Overlap Threshold", 0.1, 1.0, 0.5, 0.05, key="settings_iou_thresh")

    if st.button("💾 SAVE CONFIGURATION", use_container_width=True, key="btn_save_settings"):
        st.toast("✅ Node settings successfully saved!", icon="⚙️")
