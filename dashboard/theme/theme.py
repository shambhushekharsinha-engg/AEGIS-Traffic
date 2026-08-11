"""
AEGIS-Traffic — Theme Loader
Reads external CSS files and injects them into Streamlit with @st.cache_data for instant rendering.
"""

import os
import streamlit as st

THEME_DIR = os.path.dirname(__file__)


@st.cache_data
def load_combined_css() -> str:
    """Reads style.css, dashboard.css, and components.css into a single cached string."""
    files = ["style.css", "dashboard.css", "components.css"]
    css_content = []
    for f in files:
        path = os.path.join(THEME_DIR, f)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as file:
                css_content.append(file.read())
    return "<style>\n" + "\n".join(css_content) + "\n</style>"


def inject_theme():
    """Injects cached theme CSS into current Streamlit view."""
    st.markdown(load_combined_css(), unsafe_allow_html=True)
